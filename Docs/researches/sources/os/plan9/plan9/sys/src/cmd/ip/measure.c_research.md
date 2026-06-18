# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/measure.c

Ethernet traffic sampler that counts inbound/outbound IP bytes and packets by protocol for a target MAC address.

Key behavior:
- Opens an Ethernet device in promiscuous mode with timestamped packet capture.
- Parses Ethernet and IPv4 headers, tracking byte and packet counters for all IP, IP-in-IP/MBONE, UDP, and TCP.
- Treats packets with source MAC equal target as inbound counters named `protoin`; destination MAC equal target as outbound counters named `protoout`.
- Periodically prints timestamp, elapsed capture time, and protocol counters, then resets.
- `-s` limits sample count; `-d` prints per-packet debug.

Integration points:
- Uses Plan 9 `dial` on `<device>!-2`, control message `promiscuous`, and IP formatting helpers.

Risks and notes:
- Packet timestamp and captured length are read from fixed offsets in the Ethernet buffer (`e.d[60]`, `e.d[58]`), assuming a specific Plan 9 capture layout.
- Program labels errors as `snoopy`, likely copied from another tool.
