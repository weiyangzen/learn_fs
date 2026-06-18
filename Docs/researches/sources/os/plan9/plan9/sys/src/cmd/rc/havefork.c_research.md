# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/havefork.c

Implementation of rc process-control opcodes for systems with fork/rfork support.

Functions:
- `Xasync()` forks an async child, redirects stdin from `/dev/null`, sets `$apid`, and skips child code in parent.
- `Xpipe()` creates a pipe, forks left side, runs right side in current interpreter thread, and records pid for `Xpipewait`.
- `Xbackq()` forks command substitution, captures stdout through a pipe, splits output by `$ifs`, and pushes words.
- `Xpipefd()` implements `<{}`/`>{}` style pipefd by forking a side command and pushing `/fd/<n>`.
- `Xsubshell()` forks a subshell and waits.
- `execforkexec()` forks a child to execute an external command.

Risk/notes:
- Children call `clearwaitpids()` so inherited wait tracking does not confuse nested shells.
- `Xbackq()` uses rune-aware reading and `$ifs` matching.
- Parent/child code paths share `runq->code` and rely on `start()` to create correct frames.
