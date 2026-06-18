# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/dat.h

This header defines the execnet internal structures and shared API.

Key contents:
- `Msg`: queued output data with linked-list pointer and read pointer/end pointer.
- `Client`: per-connection state including status, pid, command, pipe fds, queued read/write requests, output messages, ioprocs, active write request, and exec request.
- External globals for client table and service object.
- Function prototypes for data reads/writes, client creation/closure, control writes, flush handling, filesystem initialization, and name customization.
- Allocation aliases to lib9p helpers: `emalloc9p`, `estrdup9p`, `erealloc9p`.
- Status enum: `Closed`, `Exec`, `Established`, `Hangup`.
- `STACK` size constant.

Important implementation notes:
- `Client.status` is surfaced through the 9P `status` file.
- The header centralizes the contract between `client.c`, `fs.c`, and `main.c`.
