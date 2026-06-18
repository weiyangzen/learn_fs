# File Research: sources/os/plan9/plan9/sys/src/cmd/ratrace.c

Threaded syscall tracer using Plan 9 `/proc`.

Main behavior:
- Can trace an existing pid or launch a command with `-c`.
- For launched commands, child calls `hang()` before `exec()` so tracing can attach before execution.
- `reader()` opens `/proc/<pid>/ctl` and `/proc/<pid>/syscall`, starts syscall tracing, reads syscall records, detects `rfork(RFPROC)` returns, and spawns readers for forked children.
- `writer()` multiplexes trace output, child fork notifications, and quit events over channels.
- `cwrite()` writes proc-control commands and signals shutdown on failure.
- `newstr()` allocates fixed trace buffers.

Risk/notes:
- Fork detection parses syscall trace text heuristically but with several checks.
- `writer()` currently increments reader count for fork events; reader spawning is performed in `reader()` itself, with an older `procrfork` line commented out.
- Trace output is written to fd 2.
