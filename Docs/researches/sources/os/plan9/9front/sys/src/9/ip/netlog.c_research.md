# File Research: sources/os/plan9/9front/sys/src/9/ip/netlog.c

Implements the IP stack action/debug log.

Key elements:
- Maintains a circular 16 KiB log buffer with blocking reads.
- Tracks open count and allocates/frees the buffer on first open/last close.
- Supports log-mask controls: `set`, `clear`, and `only`.
- Maps named flags such as `ip`, `tcp`, `udp`, `icmp`, `tcpwin`, `tcprxmt`, and `ipmsg` to bit masks.
- `netlog` appends formatted messages and wakes readers.

Dependencies:
- Used throughout the IP stack for protocol diagnostics.
- Uses Plan 9 `parsecmd`, `lookupcmd`, locks, qlocks, and rendezvous sleep/wakeup.

Research notes:
- The `only` control sets an IP address filter field, but filtering is not applied inside this file’s `netlog` function.
