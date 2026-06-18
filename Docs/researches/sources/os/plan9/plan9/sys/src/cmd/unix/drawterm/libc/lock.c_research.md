# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lock.c

This file implements low-level spin/mutex locks for the hosted libc layer.

Key behavior:
- With `PTHREAD`, locks lazily initialize a pthread mutex and use it for `lock`, `canlock`, and `unlock`.
- Without `PTHREAD`, it uses atomic test-and-set style locking with yielding.
- `ilock` and `iunlock` alias to `lock`/`unlock`.

Important details:
- Separate from kernel `QLock`; this is the low-level `Lock` primitive.
