# speed-test-vpn

Измерение скорости Outline VPN -серверов.

## Установка на сервер

```
# УСТАНОВКА
# pip install speedtest-cli

# Из-под root:
# sudo apt update
# sudo apt install shadowsocks-libev
# sudo apt install curl

# sudo apt install proxychains
# для proxychains нужен config:
# вместо: socks4  127.0.0.1 9050
# пишем: socks5 127.0.0.1 2023
```

## Алгоритм

Создание json-файла конфигурации.

`{ "server": "109.234.34.149",  "mode": "tcp_and_udp",  "server_port": 16252,  "local_address": "127.0.0.1",  "local_port": 2023,  "password": "omyp4UPGN8zGxJ8SO4p0oE",  "timeout": 86400,  "method": "chacha20-ietf-poly1305"  }`

Выполняем:

```
ss-local -v -c config.json 
```

Производим тест скачивания файла:

```
curl -x socks5h://localhost:{PORT} -O https://1090023-cf48670.tmweb.ru/{FILE}
```

Производим замер скорости:

```
proxychains speedtest-cli
```
