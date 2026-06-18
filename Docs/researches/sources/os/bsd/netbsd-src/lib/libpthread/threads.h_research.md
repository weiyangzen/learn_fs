# File Research: sources/os/bsd/netbsd-src/lib/libpthread/threads.h

This header exposes NetBSD's C11 thread API in terms of pthread types. It defines `thread_local` when needed, maps `ONCE_FLAG_INIT` to `PTHREAD_ONCE_INIT`, maps `TSS_DTOR_ITERATIONS` to `PTHREAD_DESTRUCTOR_ITERATIONS`, and typedefs C11 `cnd_t`, `thrd_t`, `tss_t`, `mtx_t`, `once_flag`, `tss_dtor_t`, and `thrd_start_t`.

It declares C11 condition variable, mutex, thread, once, and thread-specific-storage functions. It defines mutex type bits `mtx_plain`, `mtx_recursive`, `mtx_timed` and thread result constants `thrd_timedout`, `thrd_success`, `thrd_busy`, `thrd_error`, and `thrd_nomem`.

Integration points: depends on `pthread.h` for all underlying object representations and constants. Risks are API conformance gaps because the C11 ABI is intentionally layered on pthread semantics and return-code mappings.
