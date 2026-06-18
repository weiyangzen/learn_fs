# File Research: sources/os/plan9/plan9/sys/src/lib9p/listen.c

This file implements network-listening support for lib9p servers.

Key behavior:
- `_listensrv` copies a `Srv`, stores the listen address, and starts `listenproc` through the configured `_forker`.
- `listenproc` announces the address, loops accepting connections, creates a per-connection `Srv` copy, initializes connection fds and transient buffers/pools to nil, and starts `srvproc`.
- `srvproc` runs `srv`, closes the data fd, then frees the per-connection address and server copy.
- `getremotesys` reads the Plan 9 network connection `remote` file and stores the remote system prefix before `!`, defaulting to `"unknown"`.

Important dependencies:
- Requires `_forker` to have been set by `rfork.c` or `thread.c`.
- Uses Plan 9 network primitives `announce`, `listen`, and `accept`.

Notable details:
- Each accepted connection gets a shallow copy of the original `Srv`; per-connection pools and buffers are reset so `srv` allocates its own.
