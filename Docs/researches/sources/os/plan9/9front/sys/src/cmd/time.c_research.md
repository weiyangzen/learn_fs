# File Research: sources/os/plan9/9front/sys/src/cmd/time.c

This is Plan 9 `time`, executing a command and reporting user, system, and real time.

Behavior:
- Requires at least one command argument.
- Forks; child execs `argv[1]`, and if not absolute/relative, retries `/bin/<cmd>`.
- Parent waits, tolerating interrupted `wait()` calls.
- Prints `<user>u <sys>s <real>r` followed by up to several command arguments.
- Appends `# status=...` when child wait message is non-empty.
- Exits with the child wait message.

Helpers:
- `add()` appends formatted fields to a global output buffer.
- `notifyf()` continues on interrupt.
- `error()` reports syscall failures and exits.

Risk notes:
- `add()` has an old-style undeclared `static beenhere=0`; Plan 9 C accepts this style, but it is non-modern C.
- Output buffer is fixed at 4096 bytes, with `vseprint()` preventing overflow.
