# File Research: sources/os/plan9/9front/sys/src/cmd/ratrace.c

This file implements `ratrace`, a small threaded syscall tracer for Plan 9 processes.

Key responsibilities:
- Attaches to an existing pid or starts a command with `-c`.
- Opens `/proc/<pid>/ctl` and `/proc/<pid>/syscall`.
- Stops the process, enables syscall tracing with `startsyscall`, reads syscall lines, prints them to stderr, and resumes tracing.
- Detects `Rfork` syscalls with `RFPROC` and starts reader threads for newly forked child processes.
- Uses Plan 9 threads and channels:
  - `out` for syscall messages,
  - `quit` for reader termination,
  - `forkc` for child-process accounting.
- `writer()` multiplexes channels, tracks active readers, formats pid transitions, and frees messages.

Implementation notes:
- The child command path uses `hang` on its own proc ctl before `exec`, allowing the tracer to attach before execution proceeds.
- Reader failure sends the `%r` error through `quit`.
- The syscall fork detection is intentionally conservative, checking the syscall text and parsed flags.
