#!/usr/bin/env python3

from __future__ import annotations

import argparse
import configparser
import os
import re
import shutil
import socket
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

APP_NAME = "ProxyGo - v2.0"
DEFAULT_START_URL = "http://www.dnsleaktest.com"
VALID_CHAIN_MODES = ("strict_chain", "dynamic_chain", "random_chain")


class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


def color(text: str, *styles: str) -> str:
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return text
    return "".join(styles) + text + Style.RESET


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def visible_len(text: str) -> int:
    return len(ANSI_RE.sub("", text))


def terminal_width() -> int:
    return max(72, min(shutil.get_terminal_size((96, 24)).columns, 120))


def center_text(text: str, width: int | None = None) -> str:
    width = width or terminal_width()
    padding = max((width - visible_len(text)) // 2, 0)
    return " " * padding + text


def print_center(text: str = "", *styles: str) -> None:
    styled = color(text, *styles) if styles else text
    print(center_text(styled))


def clear_screen() -> None:
    if not sys.stdout.isatty():
        return
    os.system("cls" if os.name == "nt" else "clear")


def app_config_dir() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "proxygo"


def default_config_path() -> Path:
    return app_config_dir() / "config.ini"


def default_proxychains_path() -> Path:
    return app_config_dir() / "proxychains.conf"


@dataclass
class ProxyEntry:
    proxy_type: str
    host: str
    port: int
    username: str = ""
    password: str = ""

    @classmethod
    def parse(cls, value: str) -> "ProxyEntry":
        parts = value.split()
        if len(parts) not in (3, 5):
            raise ValueError(
                "Proxy entries must look like: 'socks5 127.0.0.1 9050' "
                "or 'socks5 host port username password'."
            )
        proxy_type, host, port = parts[:3]
        try:
            parsed_port = int(port)
        except ValueError as exc:
            raise ValueError(f"Proxy port must be a number, got '{port}'.") from exc
        username = parts[3] if len(parts) == 5 else ""
        password = parts[4] if len(parts) == 5 else ""
        return cls(proxy_type=proxy_type, host=host, port=parsed_port, username=username, password=password)

    def to_config_value(self) -> str:
        value = f"{self.proxy_type} {self.host} {self.port}"
        if self.username or self.password:
            value += f" {self.username} {self.password}"
        return value

    def to_proxychains_line(self) -> str:
        return self.to_config_value()

    @property
    def is_local_tor(self) -> bool:
        return self.proxy_type.lower().startswith("socks") and self.host in {"127.0.0.1", "localhost"} and self.port == 9050


@dataclass
class ProxyGoConfig:
    browser: str = "firefox"
    start_url: str = DEFAULT_START_URL
    use_proxychains: bool = True
    show_tor_status: bool = True
    stable_mode: bool = True
    tor_enabled: bool = True
    tor_service: str = "tor"
    manage_tor_service: bool = True
    stop_tor_on_exit: bool = True
    proxychains_binary: str = "proxychains4"
    proxychains_config_file: Path = field(default_factory=default_proxychains_path)
    chain_mode: str = "strict_chain"
    proxy_dns: bool = True
    quiet_mode: bool = False
    tcp_read_timeout: int = 15000
    tcp_connect_timeout: int = 8000
    proxies: list[ProxyEntry] = field(default_factory=lambda: [ProxyEntry("socks5", "127.0.0.1", 9050)])

    @classmethod
    def load(cls, path: Path) -> "ProxyGoConfig":
        if not path.exists():
            config = cls()
            config.save(path)
            return config

        parser = configparser.ConfigParser()
        parser.read(path)
        config = cls()

        config.browser = parser.get("general", "browser", fallback=config.browser)
        config.start_url = parser.get("general", "start_url", fallback=config.start_url)
        config.use_proxychains = parser.getboolean("general", "use_proxychains", fallback=config.use_proxychains)
        config.show_tor_status = parser.getboolean("general", "show_tor_status", fallback=config.show_tor_status)
        config.stable_mode = parser.getboolean("general", "stable_mode", fallback=config.stable_mode)
        config.quiet_mode = parser.getboolean("general", "quiet_mode", fallback=config.quiet_mode)

        config.tor_enabled = parser.getboolean("tor", "enabled", fallback=config.tor_enabled)
        config.tor_service = parser.get("tor", "service", fallback=config.tor_service)
        config.manage_tor_service = parser.getboolean("tor", "manage_service", fallback=config.manage_tor_service)
        config.stop_tor_on_exit = parser.getboolean("tor", "stop_on_exit", fallback=config.stop_tor_on_exit)

        config.proxychains_binary = parser.get("proxychains", "binary", fallback=config.proxychains_binary)
        config.proxychains_config_file = Path(
            os.path.expanduser(parser.get("proxychains", "config_file", fallback=str(config.proxychains_config_file)))
        )
        config.chain_mode = parser.get("proxychains", "chain_mode", fallback=config.chain_mode)
        config.proxy_dns = parser.getboolean("proxychains", "proxy_dns", fallback=config.proxy_dns)
        config.tcp_read_timeout = parser.getint("proxychains", "tcp_read_timeout", fallback=config.tcp_read_timeout)
        config.tcp_connect_timeout = parser.getint("proxychains", "tcp_connect_timeout", fallback=config.tcp_connect_timeout)

        if parser.has_section("proxies"):
            proxies: list[ProxyEntry] = []
            for _, value in sorted(parser.items("proxies")):
                try:
                    proxies.append(ProxyEntry.parse(value))
                except ValueError as exc:
                    print_notice(f"Skipping invalid proxy entry '{value}': {exc}", "warning")
            if proxies:
                config.proxies = proxies

        if config.chain_mode not in VALID_CHAIN_MODES:
            print_notice(f"Unknown chain mode '{config.chain_mode}', falling back to strict_chain.", "warning")
            config.chain_mode = "strict_chain"

        return config

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        parser = configparser.ConfigParser()
        parser["general"] = {
            "browser": self.browser,
            "start_url": self.start_url,
            "use_proxychains": str(self.use_proxychains),
            "show_tor_status": str(self.show_tor_status),
            "stable_mode": str(self.stable_mode),
            "quiet_mode": str(self.quiet_mode),
        }
        parser["tor"] = {
            "enabled": str(self.tor_enabled),
            "service": self.tor_service,
            "manage_service": str(self.manage_tor_service),
            "stop_on_exit": str(self.stop_tor_on_exit),
        }
        parser["proxychains"] = {
            "binary": self.proxychains_binary,
            "config_file": str(self.proxychains_config_file),
            "chain_mode": self.chain_mode,
            "proxy_dns": str(self.proxy_dns),
            "tcp_read_timeout": str(self.tcp_read_timeout),
            "tcp_connect_timeout": str(self.tcp_connect_timeout),
        }
        parser["proxies"] = {str(index): proxy.to_config_value() for index, proxy in enumerate(self.proxies, start=1)}
        with path.open("w", encoding="utf-8") as config_file:
            parser.write(config_file)

    def effective_command(self) -> list[str]:
        app_command = [self.browser, self.start_url]
        if not self.use_proxychains:
            return app_command
        return [self.proxychains_binary, "-f", str(self.proxychains_config_file), *app_command]

    @property
    def using_tor_proxy(self) -> bool:
        return any(proxy.is_local_tor for proxy in self.proxies)


def print_banner() -> None:
    print()
    panel(
        APP_NAME.upper(),
        [
    "      ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗ ██████╗  ██████╗ ",
    "      ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝██╔════╝ ██╔═══██╗",
    "      ██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝ ██║  ███╗██║   ██║",
    "      ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝  ██║   ██║██║   ██║",
    "      ██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║   ╚██████╔╝╚██████╔╝",
    "      ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ",
    "",
    "                       Advanced Proxy Controller",
    "           Tor • Proxychains • Stable Profiles • Diagnostics",
        ],
        Style.CYAN,
        width=74,
        align="left",
    )
    print()


def format_status(value: bool, true_text: str = "enabled", false_text: str = "disabled") -> str:
    return f"✓ {true_text}" if value else f"! {false_text}"


def print_notice(message: str, level: str = "info") -> None:
    palette = {
        "info": Style.CYAN,
        "success": Style.GREEN,
        "warning": Style.YELLOW,
        "error": Style.RED,
    }
    icon = {"info": "•", "success": "✓", "warning": "!", "error": "✗"}.get(level, "•")
    panel(level.upper(), [f"{icon} {message}"], palette.get(level, Style.CYAN))


def panel(
    title: str,
    rows: Iterable[str],
    border_color: str = Style.CYAN,
    *,
    width: int | None = None,
    align: str = "left",
) -> None:
    rows = [str(row) for row in rows]
    term_width = terminal_width()
    content_width = max([visible_len(title), *(visible_len(row) for row in rows), 56])
    width = min(width or content_width + 4, term_width - 4)
    width = max(width, 60)
    inner_width = width - 4
    indent = " " * max((term_width - width) // 2, 0)

    def border(left: str, fill: str, right: str) -> str:
        return indent + color(left + fill * (width - 2) + right, border_color, Style.BOLD)

    print(border("╔", "═", "╗"))
    title_text = f" {title} "
    title_pad_left = max((width - 2 - visible_len(title_text)) // 2, 0)
    title_pad_right = max(width - 2 - visible_len(title_text) - title_pad_left, 0)
    print(
        indent
        + color("║", border_color, Style.BOLD)
        + " " * title_pad_left
        + color(title_text, Style.BOLD)
        + " " * title_pad_right
        + color("║", border_color, Style.BOLD)
    )
    print(border("╠", "═", "╣"))

    for row in rows:
        wrapped = textwrap.wrap(row, width=inner_width, replace_whitespace=False) or [""]
        for line in wrapped:
            if align == "center":
                left_pad = max((inner_width - visible_len(line)) // 2, 0)
                right_pad = max(inner_width - visible_len(line) - left_pad, 0)
                formatted = " " * left_pad + line + " " * right_pad
            else:
                formatted = line + " " * max(inner_width - visible_len(line), 0)
            print(indent + color("║ ", border_color, Style.BOLD) + formatted + color(" ║", border_color, Style.BOLD))
    print(border("╚", "═", "╝"))


def prompt_line(label: str) -> str:
    return center_text(color(label, Style.CYAN, Style.BOLD))


def pause(message: str = "Press Enter to continue...") -> None:
    input(prompt_line(message))


def run_command(command: list[str], *, capture: bool = False, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=capture, text=True, check=check)


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def service_is_active(service: str) -> bool:
    if not command_exists("systemctl"):
        return False
    result = run_command(["systemctl", "is-active", "--quiet", service], capture=True)
    return result.returncode == 0


def start_tor(config: ProxyGoConfig) -> bool:
    if not config.tor_enabled or not config.manage_tor_service:
        return False
    if service_is_active(config.tor_service):
        print_notice(f"Tor service '{config.tor_service}' is already running.", "success")
        return False
    print_notice(f"Starting Tor service '{config.tor_service}'...", "info")
    result = run_command(["sudo", "systemctl", "start", config.tor_service], capture=True)
    if result.returncode != 0:
        print_notice("Failed to start Tor.", "error")
        print(result.stderr.strip())
        raise SystemExit(result.returncode)
    print_notice("Tor started.", "success")
    return True


def stop_tor(config: ProxyGoConfig, tor_started_by_proxygo: bool) -> None:
    if not config.tor_enabled or not config.manage_tor_service or not config.stop_tor_on_exit:
        return
    if not tor_started_by_proxygo:
        print_notice("Tor was already running before ProxyGo started; leaving it running.", "warning")
        return
    print_notice(f"Stopping Tor service '{config.tor_service}'...", "info")
    result = run_command(["sudo", "systemctl", "stop", config.tor_service], capture=True)
    if result.returncode == 0:
        print_notice("Tor stopped.", "success")
    else:
        print_notice("Failed to stop Tor cleanly.", "error")
        print(result.stderr.strip())


def tor_port_reachable(proxies: list[ProxyEntry]) -> bool:
    tor_proxies = [proxy for proxy in proxies if proxy.is_local_tor]
    if not tor_proxies:
        return False
    proxy = tor_proxies[0]
    try:
        with socket.create_connection((proxy.host, proxy.port), timeout=2):
            return True
    except OSError:
        return False


def write_proxychains_config(config: ProxyGoConfig) -> Path:
    config.proxychains_config_file.parent.mkdir(parents=True, exist_ok=True)
    if config.stable_mode and config.chain_mode != "strict_chain":
        print_notice("Stable mode works best with strict_chain. Writing strict_chain for this run.", "warning")
        chain_mode = "strict_chain"
    else:
        chain_mode = config.chain_mode

    lines = [
        "# Generated by ProxyGo. Edit ~/.config/proxygo/config.ini instead of this file.",
        chain_mode,
    ]
    if config.proxy_dns:
        lines.append("proxy_dns")
    lines.extend(
        [
            f"tcp_read_time_out {config.tcp_read_timeout}",
            f"tcp_connect_time_out {config.tcp_connect_timeout}",
            "",
            "[ProxyList]",
        ]
    )
    lines.extend(proxy.to_proxychains_line() for proxy in config.proxies)
    config.proxychains_config_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config.proxychains_config_file


def show_status(config: ProxyGoConfig) -> None:
    rows = [
        f"Browser             {config.browser} ({'found' if command_exists(config.browser) else 'missing'})",
        f"Start URL           {config.start_url}",
        f"Proxychains         {config.proxychains_binary} ({'found' if command_exists(config.proxychains_binary) else 'missing'})",
        f"Generated config    {config.proxychains_config_file}",
        f"Chain mode          {config.chain_mode}",
        f"Proxy DNS           {format_status(config.proxy_dns)}",
        f"Stable mode         {format_status(config.stable_mode)}",
        f"Tor service         {config.tor_service} ({'active' if service_is_active(config.tor_service) else 'inactive'})",
        f"Tor SOCKS port      {'reachable' if tor_port_reachable(config.proxies) else 'not reachable / not configured'}",
        "",
        "Proxy list",
    ]
    rows.extend(f"  {index:02d}. {proxy.to_config_value()}" for index, proxy in enumerate(config.proxies, start=1))
    panel("ProxyGo Status", rows)
    if config.using_tor_proxy:
        print_notice("Tor can change circuits/exits even when proxychains stays on 127.0.0.1:9050.", "warning")


def validate_dependencies(config: ProxyGoConfig) -> None:
    missing: list[str] = []
    if not command_exists(config.browser):
        missing.append(config.browser)
    if config.use_proxychains and not command_exists(config.proxychains_binary):
        missing.append(config.proxychains_binary)
    if config.tor_enabled and config.manage_tor_service and not command_exists("systemctl"):
        missing.append("systemctl")
    if missing:
        raise SystemExit(color(f"Missing required command(s): {', '.join(missing)}", Style.RED, Style.BOLD))


def warn_about_stability(config: ProxyGoConfig) -> None:
    warnings: list[str] = []
    if config.chain_mode != "strict_chain":
        warnings.append(f"{config.chain_mode} can change proxy behavior when multiple proxies are configured.")
    if len(config.proxies) > 1 and config.stable_mode:
        warnings.append("Stable mode is strongest with a single proxy entry.")
    if config.using_tor_proxy:
        warnings.append("Tor may rotate circuits/exits; use a fixed proxy when endpoint consistency is required.")
    for warning in warnings:
        print_notice(warning, "warning")


def run_session(config: ProxyGoConfig, *, dry_run: bool = False) -> int:
    if config.use_proxychains:
        write_proxychains_config(config)
    command = config.effective_command()
    warn_about_stability(config)
    if dry_run:
        panel("Dry Run Command", [" ".join(command)], Style.MAGENTA)
        return 0

    validate_dependencies(config)
    tor_started_by_proxygo = False
    try:
        if config.tor_enabled:
            tor_started_by_proxygo = start_tor(config)
            time.sleep(1)
            if config.show_tor_status:
                result = run_command(["systemctl", "--no-pager", "status", config.tor_service], capture=True)
                print(result.stdout.strip() or result.stderr.strip())
        print_notice("Launching session through ProxyGo...", "success")
        panel("Launch Command", [" ".join(command)], Style.MAGENTA)
        process = subprocess.Popen(command)
        return process.wait()
    except KeyboardInterrupt:
        print_notice("Session interrupted by user.", "error")
        return 130
    finally:
        stop_tor(config, tor_started_by_proxygo)


def prompt(default: str, label: str) -> str:
    value = input(prompt_line(f"{label} [{default}]: ")).strip()
    return value or default


def prompt_bool(default: bool, label: str) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = input(prompt_line(f"{label} [{suffix}]: ")).strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "true", "1", "on"}


def configure_general(config: ProxyGoConfig, path: Path) -> None:
    config.browser = prompt(config.browser, "Browser command")
    config.start_url = prompt(config.start_url, "Start/test URL")
    config.stable_mode = prompt_bool(config.stable_mode, "Enable stable-session warnings/defaults")
    config.show_tor_status = prompt_bool(config.show_tor_status, "Show Tor status before launch")
    config.save(path)
    print_notice(f"Saved {path}", "success")


def configure_proxychains(config: ProxyGoConfig, path: Path) -> None:
    config.proxychains_binary = prompt(config.proxychains_binary, "Proxychains binary")
    config.proxychains_config_file = Path(os.path.expanduser(prompt(str(config.proxychains_config_file), "Generated proxychains config path")))
    panel("Chain Mode", [f"{index}. {mode}" for index, mode in enumerate(VALID_CHAIN_MODES, start=1)])
    selection = prompt(str(VALID_CHAIN_MODES.index(config.chain_mode) + 1), "Mode")
    if selection.isdigit() and 1 <= int(selection) <= len(VALID_CHAIN_MODES):
        config.chain_mode = VALID_CHAIN_MODES[int(selection) - 1]
    elif selection in VALID_CHAIN_MODES:
        config.chain_mode = selection
    config.proxy_dns = prompt_bool(config.proxy_dns, "Enable proxy_dns")
    config.save(path)
    write_proxychains_config(config)
    print_notice(f"Saved {path} and generated {config.proxychains_config_file}", "success")


def manage_proxies(config: ProxyGoConfig, path: Path) -> None:
    while True:
        clear_screen()
        panel(
            "Proxy List",
            [*(f"{index}. {proxy.to_config_value()}" for index, proxy in enumerate(config.proxies, start=1)), "", "a. Add proxy", "r. Remove proxy", "b. Back"],
        )
        choice = input(prompt_line("Select: ")).strip().lower()
        if choice == "a":
            value = input(prompt_line("Proxy entry (example: socks5 127.0.0.1 9050): ")).strip()
            try:
                config.proxies.append(ProxyEntry.parse(value))
                config.save(path)
                write_proxychains_config(config)
            except ValueError as exc:
                print_notice(str(exc), "error")
                pause()
        elif choice == "r":
            index = input(prompt_line("Proxy number to remove: ")).strip()
            if index.isdigit() and 1 <= int(index) <= len(config.proxies):
                config.proxies.pop(int(index) - 1)
                if not config.proxies:
                    config.proxies.append(ProxyEntry("socks5", "127.0.0.1", 9050))
                config.save(path)
                write_proxychains_config(config)
        elif choice == "b":
            return


def diagnostics(config: ProxyGoConfig) -> None:
    show_status(config)
    checks = [
        ("Browser command", command_exists(config.browser)),
        ("Proxychains command", command_exists(config.proxychains_binary)),
        ("Generated proxychains config", config.proxychains_config_file.exists()),
        ("Tor service active", service_is_active(config.tor_service)),
        ("Tor SOCKS reachable", tor_port_reachable(config.proxies)),
    ]
    rows = []
    for name, passed in checks:
        symbol = "✓" if passed else "!"
        state = "PASS" if passed else "CHECK"
        rows.append(f"{symbol} {state:<5} {name}")
    print()
    panel("Diagnostics", rows, Style.MAGENTA)


def menu(config: ProxyGoConfig, path: Path) -> None:
    while True:
        clear_screen()
        print_banner()
        panel(
            "Main Menu",
            [
                f"Current profile   {config.browser} → {config.start_url}",
                f"Chain mode        {config.chain_mode} | Stable mode: {config.stable_mode}",
                "",
                "  1  Run ProxyGo session",
                "  2  Status dashboard",
                "  3  General settings",
                "  4  Proxychains settings",
                "  5  Manage proxy list",
                "  6  Generate proxychains config",
                "  7  Diagnostics",
                "  8  Start Tor service",
                "  9  Stop Tor service",
                "  0  Exit",
            ],
        )
        choice = input(prompt_line("Select an option: ")).strip()
        if choice == "1":
            run_session(config)
            pause("Press Enter to return to menu...")
        elif choice == "2":
            clear_screen()
            show_status(config)
            pause("Press Enter to return to menu...")
        elif choice == "3":
            configure_general(config, path)
            pause("Press Enter to return to menu...")
        elif choice == "4":
            configure_proxychains(config, path)
            pause("Press Enter to return to menu...")
        elif choice == "5":
            manage_proxies(config, path)
        elif choice == "6":
            generated = write_proxychains_config(config)
            print_notice(f"Generated {generated}", "success")
            pause("Press Enter to return to menu...")
        elif choice == "7":
            clear_screen()
            diagnostics(config)
            pause("Press Enter to return to menu...")
        elif choice == "8":
            start_tor(config)
            pause("Press Enter to return to menu...")
        elif choice == "9":
            run_command(["sudo", "systemctl", "stop", config.tor_service])
            pause("Press Enter to return to menu...")
        elif choice == "0":
            return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Advanced menu-driven Tor/proxychains launcher.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            f"""
            Examples:
              proxygo                    Open the full menu
              proxygo run                Launch using saved settings
              proxygo status             Show current dashboard
              proxygo init-config        Create ~/.config/proxygo/config.ini
              proxygo generate-config    Write the proxychains config used by ProxyGo
              proxygo run --dry-run      Print the launch command without running it
            """
        ),
    )
    parser.add_argument("--config", type=Path, default=default_config_path(), help="Path to ProxyGo config.ini")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a ProxyGo session")
    run_parser.add_argument("--url", help="Override the configured start URL for this run")
    run_parser.add_argument("--browser", help="Override the configured browser for this run")
    run_parser.add_argument("--dry-run", action="store_true", help="Print the command without running it")
    run_parser.add_argument("--no-tor", action="store_true", help="Do not start or stop the Tor service")

    subparsers.add_parser("menu", help="Open the interactive menu")
    subparsers.add_parser("status", help="Show status dashboard")
    subparsers.add_parser("init-config", help="Create or refresh the default config file")
    subparsers.add_parser("generate-config", help="Generate the proxychains config file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(os.path.expanduser(str(args.config)))
    config = ProxyGoConfig.load(config_path)

    if args.command == "init-config":
        config.save(config_path)
        write_proxychains_config(config)
        print_notice(f"Created {config_path}", "success")
        print_notice(f"Created {config.proxychains_config_file}", "success")
        return 0
    if args.command == "generate-config":
        generated = write_proxychains_config(config)
        print_notice(f"Generated {generated}", "success")
        return 0
    if args.command == "status":
        show_status(config)
        return 0
    if args.command == "run":
        if args.url:
            config.start_url = args.url
        if args.browser:
            config.browser = args.browser
        if args.no_tor:
            config.tor_enabled = False
        return run_session(config, dry_run=args.dry_run)

    menu(config, config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
