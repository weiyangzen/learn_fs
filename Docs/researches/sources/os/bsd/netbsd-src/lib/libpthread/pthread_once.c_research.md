# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_once.c

This file implements `pthread_once`. It uses the mutex embedded in `pthread_once_t` to serialize initialization and `pto_done` as the completion flag. If `pto_done` is clear, it locks the mutex, pushes a cleanup handler to unlock on cancellation/unwind, checks `pto_done` again, calls the routine, issues a release barrier, sets `pto_done`, and pops cleanup with execute. If already done, it issues an acquire barrier before returning.

The implementation falls back to libc stub behavior when `__uselibcstub` is set and exports a strong alias to `__libc_thr_once`.

Integration points: depends on mutexes and pthread cleanup macros. Risks are routine cancellation or nonlocal exit before setting `pto_done`, for which the cleanup handler at least releases the mutex, and correct release/acquire visibility for initialized data.
