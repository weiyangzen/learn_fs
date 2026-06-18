# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nblistener.c

UDP announce helper for NetBIOS services.

Key function:
- `nbudpannounce` announces `udp!*!<port>`, enables Plan 9 UDP header mode, opens the data file, stores the data fd, and sets `nbudphdrsize`.

Interactions:
- Used by NBNS and datagram listeners.

Notable details:
- Returns string literals on failure rather than setting `werrstr`.
- Leaves the announce ctl fd closed after data fd open.
