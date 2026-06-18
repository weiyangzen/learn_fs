# File Research: sources/os/bsd/netbsd-src/lib/libpthread/cnd.c

## Purpose
Implements C11 condition variable APIs over pthread condition variables.

## Main Responsibilities
- Maps `cnd_broadcast`, `cnd_signal`, `cnd_wait`, and `cnd_timedwait` to pthread condition APIs.
- Maps `cnd_init` and `cnd_destroy` to pthread condition init/destroy.
- Converts pthread return codes to C11 `thrd_success`, `thrd_error`, or `thrd_timedout`.

## Dependencies
- `pthread.h`, `threads.h`, `errno.h`.
