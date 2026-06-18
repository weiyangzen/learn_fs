# File Research: sources/os/plan9/plan9/sys/src/lib9p/post.c

This file implements posting and optional mounting of a lib9p server through a pipe.

Key behavior:
- `_postmountsrv` creates a pipe unless `Srv.nopipe` is set, assigns server and kernel-side fds, and optionally posts the server fd in `/srv`.
- Starts `postproc` through `_forker` with `RFNAMEG`.
- Unless `leavefdsopen` is set, it switches fd groups, synchronizes with the server process via `rendezvous`, and closes server-side pipe fds before mounting.
- If a mount point is provided, it mounts with `amount`; otherwise it closes `srvfd`.
- `postproc` optionally isolates note group/fd handling, closes the kernel-side fd, and runs `srv`.

Important dependencies:
- Requires `_forker` set by process or thread wrappers.
- Uses `postfd` from `srv.c`.

Notable details:
- The long comment documents the fd-lifetime issue: keeping the server half open in the mounting process can make a mount hang after server death.
- `leavefdsopen` is an escape hatch for programs where fd bookkeeping is impractical.
