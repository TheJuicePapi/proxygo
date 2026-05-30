<img width="1536" height="1024" alt="proxygo Image May 13, 2026, 02_03_24 PM" src="https://github.com/user-attachments/assets/6aad3096-8c46-46e8-9ed9-0e0f3ebdb8e0" />

## ProxyGo

ProxyGo is an advanced, menu-driven Tor/proxychains controller for Linux. It can start Tor, generate a dedicated proxychains configuration, launch a browser through the selected proxy chain, and clean up when the session ends.

The original one-button launcher has been reworked into a configurable tool with a dashboard, visual menu system, stable-session warnings, generated proxychains configs, and command-line controls.

<img width="821" height="671" alt="Proxygo1-1" src="https://github.com/user-attachments/assets/bf9b6d9c-0c60-470c-86df-89836ae0ef82" />
<img width="828" height="676" alt="Proxygo2-1" src="https://github.com/user-attachments/assets/4d095272-772e-4c9c-925e-72d2df4deb6e" />
<img width="826" height="672" alt="Proxygo3-1" src="https://github.com/user-attachments/assets/f90c0220-d631-435f-88c4-6a7055c376d0" />
<img width="841" height="675" alt="Proxygo4" src="https://github.com/user-attachments/assets/9983dde3-f6a2-4406-aa7f-6415f58f9c8e" />


## Features

- Full interactive terminal menu with centered, polished visual panels.
- Status dashboard for Tor, proxychains, browser, generated config, and proxy list.
- Dedicated ProxyGo config at `~/.config/proxygo/config.ini`.
- Generated proxychains config at `~/.config/proxygo/proxychains.conf`.
- Launches proxychains with `-f` so ProxyGo always uses the config it generated.
- Configurable browser command and start/test URL.
- Configurable proxychains binary, chain mode, DNS proxying, and timeouts.
- Proxy list manager for SOCKS/HTTP proxy entries.
- Stable-session mode warnings for chain modes, multiple proxies, and Tor circuit behavior.
- CLI commands for scripting and power users.
- No third-party Python packages required.

## Important note about stability

ProxyGo can make proxychains more predictable by using `strict_chain` and a generated config file, but Tor can still rotate circuits or exits behind `127.0.0.1:9050`. If endpoint consistency is required for a legitimate account/session workflow, use a single fixed proxy instead of expecting Tor to keep the same exit forever.

## Installation

```bash
git clone https://github.com/WastelandSYS/proxygo.git
cd proxygo
sudo chmod +x install.sh proxygo.py
sudo ./install.sh
```

The installer installs `tor`, `proxychains4`, and `python3`, copies ProxyGo to `/usr/local/bin/proxygo`, and creates the default config for your user.

Manual dependency installation:

```bash
sudo apt-get update
sudo apt-get install -y tor proxychains4 python3
```

## Usage

Open the advanced menu:

```bash
proxygo
```

Run with saved settings:

```bash
proxygo run
```

Show the status dashboard:

```bash
proxygo status
```

Create or refresh default config files:

```bash
proxygo init-config
```

Generate the proxychains config only:

```bash
proxygo generate-config
```

Dry-run the launch command:

```bash
proxygo run --dry-run
```

Override the browser or URL for one run:

```bash
proxygo run --browser firefox --url http://www.dnsleaktest.com
```

Run without managing Tor:

```bash
proxygo run --no-tor
```

## Configuration

ProxyGo stores its main settings here:

```text
~/.config/proxygo/config.ini
```

Default example:

```ini
[general]
browser = firefox
start_url = http://www.dnsleaktest.com
use_proxychains = True
show_tor_status = True
stable_mode = True
quiet_mode = False

[tor]
enabled = True
service = tor
manage_service = True
stop_on_exit = True

[proxychains]
binary = proxychains4
config_file = ~/.config/proxygo/proxychains.conf
chain_mode = strict_chain
proxy_dns = True
tcp_read_timeout = 15000
tcp_connect_timeout = 8000

[proxies]
1 = socks5 127.0.0.1 9050
```

ProxyGo generates this file from your settings:

```text
~/.config/proxygo/proxychains.conf
```

Generated example:

```text
strict_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 9050
```

ProxyGo launches sessions with:

```bash
proxychains4 -f ~/.config/proxygo/proxychains.conf firefox http://www.dnsleaktest.com
```

That means you no longer need to edit `/etc/proxychains4.conf` for normal ProxyGo use.

## Chain modes

- `strict_chain`: Uses the proxy list in order. Best default for stable sessions.
- `dynamic_chain`: Skips unavailable proxies. Useful for fallback, but less predictable.
- `random_chain`: Randomizes proxy selection. Not recommended for session consistency.

## Proxy entries

Proxy entries use proxychains format:

```text
socks5 127.0.0.1 9050
http 192.168.1.50 8080
socks5 proxy.example.com 1080 username password
```

You can add or remove proxy entries from the interactive menu.

## Responsible use

ProxyGo is intended for privacy testing, lab work, routing control, and learning how Tor/proxychains behave. Use it responsibly and follow the rules of any network or service you access.
