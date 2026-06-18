# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/util.c

Shared secstore utility functions. `emalloc`, `erealloc`, and `estrdup` are fatal-on-failure helpers. `getpassm` reads hidden console input in raw mode while keeping console fds open for ssh-environment reliability.

`validatefile` rejects nil/empty names, `..`, overly long names, control characters, and `/`, logging illegal names to the secstore log.
