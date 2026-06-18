# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/client.c

Client/process state engine for the `execnet` synthetic network filesystem.

Key behavior:
- Allocates reusable `Client` records with reader/writer I/O procs and command state.
- Implements queued 9P read requests, queued write requests, and queued process-output messages; `matchmsgs()` pairs reads with buffered output.
- `ctlwrite()` accepts `connect <addr>` and `hangup`; connect converts `host!svc`-style text into `exec <addr>` and starts `/bin/rc -c`.
- `execproc()` creates a pipe, attaches it to child stdin/stdout, closes inherited fds, and execs rc.
- Separate read/write threads transfer between 9P `data` reads/writes and the command pipe.
- Flush handling removes queued reads/writes or interrupts active I/O.
- Close/hangup kills the child process and responds to pending requests with hangup.

Filesystem relevance:
- Implements the dynamic behavior behind `/net/exec/N/{ctl,data,...}` files.
