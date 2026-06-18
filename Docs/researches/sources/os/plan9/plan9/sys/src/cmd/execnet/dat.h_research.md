# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/dat.h

Shared state header for `execnet`.

Key contents:
- `Msg` buffers process output for pending reads.
- `Client` tracks process lifecycle, command string, pipe fds, pid, status, queued 9P read/write requests, message queues, I/O procs, writer kick channel, and pending exec request.
- Declares client APIs, filesystem initialization, and exec directory naming.
- Defines stack size and client status enum: `Closed`, `Exec`, `Established`, `Hangup`.

Filesystem relevance:
- Defines in-memory state for the synthetic `/net/exec` 9P filesystem.
