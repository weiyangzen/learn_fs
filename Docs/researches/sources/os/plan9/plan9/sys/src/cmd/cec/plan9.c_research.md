# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/plan9.c

This file implements Plan 9 network-file access for `cec`.

Key behavior:
- `netopen0()` opens `<interface>/clone`, reads the conversation number, writes `connect <etype>`, opens conversation `ctl`, enables nonblocking mode, then opens conversation `data`.
- `netopen()` wraps `netopen0()` with cleanup and error reporting.
- `netclose()` closes clone/control/data fds.
- `netget()` reads packets from the data fd and optionally dumps them under debug.
- `netsend()` writes packets to the data fd, padding short Ethernet frames to 60 bytes.

Important details:
- Global `fd` is the active network data fd used by the main loop.
- The control fd is set nonblocking so receive timeouts can be driven by alarms.
- Packet dumping uses shared `dump()`.

Filesystem relevance:
- Direct Plan 9 namespace use: opens and controls `/net/ether*/clone`, `ctl`, and `data` files.
