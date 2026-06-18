# File Research: sources/os/bsd/netbsd-src/lib/libpthread/mtx.c

## Purpose
Implements C11 mutex APIs over pthread mutexes.

## Main Responsibilities
- Maps destroy, lock, timedlock, trylock, and unlock to pthread mutex APIs.
- Implements plain/timed mutex init with default pthread mutex attributes.
- Implements recursive mutex init with `PTHREAD_MUTEX_RECURSIVE`.
- Converts pthread return codes to C11 `thrd_success`, `thrd_error`, `thrd_timedout`, or `thrd_busy`.

## Key Implementation Notes
- `mtx_destroy()` ignores pthread destroy return because C11 destroy returns `void`.
- `mtx_init()` accepts `mtx_plain`, `mtx_timed`, and each combined with `mtx_recursive`.

## Dependencies
- `pthread.h`, `threads.h`, `errno.h`.
