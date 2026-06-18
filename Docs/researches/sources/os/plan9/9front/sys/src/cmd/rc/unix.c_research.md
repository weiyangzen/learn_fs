# File Research: sources/os/plan9/9front/sys/src/cmd/rc/unix.c

Unix portability backend for `rc`. Mirrors the Plan 9 backend with Unix syscalls and environment representation.

Variables become environment strings using `=` and an internal separator for list values; functions are exported as special `#()fn name body` strings. `finit` reads compatible function definitions from `environ`.

Implements Unix signal setup, wait status conversion, `execve`, `fork`, `opendir/readdir`, fd operations, temporary unlink-on-open behavior for here-docs, and tty/prompt handling.
