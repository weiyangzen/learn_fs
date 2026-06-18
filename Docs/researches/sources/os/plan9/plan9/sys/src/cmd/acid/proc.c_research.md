# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/proc.c

This file manages Acid’s attachment to Plan 9 processes through `/proc`.

Key behavior:
- `sproc(pid)` opens `/proc/<pid>/mem`, validates text identity, builds `cormap` with `attachproc`, renames text/data segments, records `pid`, and installs the process in Acid’s process table.
- `nproc(argv)` forks a child, hangs it through `/proc/<pid>/ctl`, execs the target, then attaches Acid to the stopped child.
- `msg(pid, msg)` writes process-control commands to stored `/proc/<pid>/ctl` fds.
- `notes(pid)` reads pending notes from `/proc/<pid>/note` into Acid variable `notes`.
- `getstatus(pid)` parses `/proc/<pid>/status`.
- `waitfor(pid)` waits for a specific child wait message.

Important details:
- Attached process state is tracked in `ptab` and mirrored in Acid variables `pid` and `proclist`.
- `nocore()` closes segment fds in the current `cormap`.
- If control writes fail with `"process exited"`, `msg()` deinstalls the pid before reporting the error.

Filesystem relevance:
- Direct use of Plan 9’s process filesystem: `/proc/<pid>/mem`, `ctl`, `note`, and `status` are core interfaces.
