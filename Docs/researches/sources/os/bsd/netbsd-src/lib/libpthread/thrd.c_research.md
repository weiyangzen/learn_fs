# File Research: sources/os/bsd/netbsd-src/lib/libpthread/thrd.c

This file implements C11 `<threads.h>` thread functions as thin wrappers over pthreads. `thrd_create` allocates a small trampoline cookie holding the C11 start function and argument, creates a pthread running `__thrd_create_tramp`, and maps `pthread_create` errors to `thrd_success`, `thrd_nomem`, or `thrd_error`. The trampoline calls the C11 function, frees the cookie, and returns the integer result through a pointer-sized cast.

Other wrappers are direct: current/equal/detach/join/exit map to pthread equivalents, `thrd_join` translates the returned pointer-sized integer back to `int`, `thrd_sleep` uses `clock_nanosleep(CLOCK_MONOTONIC, TIMER_RELTIME, ...)` and maps interrupt/other errors to C11 return conventions, and `thrd_yield` calls `sched_yield`.

Integration points: paired with `threads.h`, `mtx.c`, `cnd.c`, `tss.c`, and pthread lifecycle APIs. Risks are pointer/integer result casting portability, cookie allocation failure, and C11 return-code translation losing detailed pthread errno values.
