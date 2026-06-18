# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_kevent.c

Read completely: 103 lines.

This implements compatibility `kevent` and `__kevent50`. `kevent` converts an optional `timespec50` timeout and calls `__kevent50`; `__kevent50` allocates native `struct kevent` arrays, converts input `kevent100` changes, calls `__kevent100`, then converts returned events back to `kevent100`.

Important interactions: bridges old kqueue event layout to the current one.

Security/reliability notes: allocation sizes are `sizeof(*event) * count` without an explicit overflow check. A zero-count `malloc(0)` returning NULL would be treated as failure on platforms with that behavior.
