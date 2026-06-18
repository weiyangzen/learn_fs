# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/srv.c

Purpose: Per-connection 9P stream handling for cwfs.

Key structures:
- `Srv`: reference-counted per-channel state with `Chan*` and fd.
- `freechans`: global free list of preallocated channels.

Important behavior:
- `srvinit()` preallocates `Nchans` channels, each with embedded `Srv` state.
- `srvchan()` takes an accepted fd/name, removes a channel from the free list, initializes connection metadata, creates a reply queue/output process if needed, and starts an input process.
- `srvi()` reads a byte stream, frames 9P2000 messages by their little-endian size header, allocates small or large `Msgbuf`s, and sends them to `serveq`.
- `srvo()` receives replies from a channel reply queue and writes them back to the connection fd, handling interrupts and hangups.
- `chanhangup()` frees file state for the channel and attempts to write `hangup` to the connection ctl file.
- `srvput()` decrements refs, closes fd, frees files, and returns the channel to the free list.

Notable details:
- `srv.c` owns transport framing; protocol dispatch happens in `main.c:serve()`.
- Reference counting keeps the fd alive while queued replies are outstanding.
