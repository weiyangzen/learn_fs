# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/process.c

This file wraps child process launch and pipe management.

Key behavior:
- `instream` creates a parent-write/child-read pipe with a `Biobuf`.
- `outstream` creates a child-write/parent-read pipe with a `Biobuf`.
- `stream_free` closes both child fd and buffered parent fd.
- `noshell_proc_start` forks, optionally detaches, wires standard fds from streams, closes extra fds, optionally calls `become`, and execs argv.
- `proc_start` runs a command through `/bin/rc -c`.
- `proc_wait` waits for the tracked pid and stores status.
- `proc_free` frees streams, waits if needed, and releases wait message.

Integration and risks:
- The child fd-closing loop uses `sysfiles()` from `libsys.c`.
- `proc_free` waits for live children, so callers must avoid deadlocks with unconsumed pipe output.
