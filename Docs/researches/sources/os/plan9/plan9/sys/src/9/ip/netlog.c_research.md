# File Research: sources/os/plan9/plan9/sys/src/9/ip/netlog.c

Implements the per-stack network debug log exposed through the `log` file.

Key responsibilities:
- `netloginit` allocates the `Netlog` object.
- `netlogopen` lazily allocates a 16 KiB circular buffer and tracks open count.
- `netlogclose` decrements opens and frees the buffer on last close.
- `netlogread` blocks until data is available, then copies from the circular buffer with wrap handling.
- `netlogctl` parses `set`, `clear`, and `only` control commands to manage logging masks and optional IP filtering address.
- `netlog` formats messages, drops oldest bytes on overflow, appends into the circular buffer, and wakes readers.

Supported flags:
- `ppp`, `ip`, `fs`, `tcp`, `icmp`, `udp`, `compress`, `gre`, `tcpwin`, `tcprxmt`, `udpmsg`, `ipmsg`, and `esp`.

Notable behavior:
- Logging is skipped unless the relevant mask is enabled and the log file is open.
