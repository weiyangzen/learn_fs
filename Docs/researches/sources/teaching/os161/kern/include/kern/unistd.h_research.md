# File Research: sources/teaching/os161/kern/include/kern/unistd.h

Defines standard file descriptor constants.

Constants:
- `STDIN_FILENO` 0
- `STDOUT_FILENO` 1
- `STDERR_FILENO` 2

Relevance:
- Part of syscall/user ABI; not directly used by SFS or semfs internals.
