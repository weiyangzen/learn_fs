# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/event.c

This file starts the hosted shell process and integrates it with Plan 9's event library.

Key functions:
- `edie` closes `outfd` and posts `exit` to the current process group once.
- `start_host` initializes console control via `consctl`, forks a hosted `/bin/rc` process in a new namespace/fd/note group, wires its stdio to `/dev/cons`, and returns the writable host side `/mnt/cons/cons/data`.
- `ebegin` registers `edie`, initializes mouse/keyboard events, starts the host, and registers the host fd as an event source using `estart`.
- `send_interrupt` posts an `interrupt` note to the hosted shell process group.

Role:
- Bridges the GUI terminal event loop with a child shell's console I/O.
