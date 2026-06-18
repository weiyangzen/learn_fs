# File Research: sources/os/bsd/netbsd-src/lib/libpthread/tss.c

This file implements the C11 thread-specific storage functions as wrappers over pthread TSD. `tss_create` validates the output pointer with `_DIAGASSERT`, calls `pthread_key_create`, and maps success to `thrd_success` and failure to `thrd_error`. `tss_delete` calls `pthread_key_delete` and discards the result because C11 specifies no return value. `tss_get` returns `pthread_getspecific`, and `tss_set` maps `pthread_setspecific` success or failure to C11 return codes.

Integration points: paired with `threads.h` and `pthread_tsd.c`. Risks are minimal, mostly loss of detailed pthread error values and the C11 no-return-value delete behavior hiding invalid-key failures.
