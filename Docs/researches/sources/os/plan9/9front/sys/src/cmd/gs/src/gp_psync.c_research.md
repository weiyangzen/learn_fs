# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_psync.c

POSIX pthread synchronization and detached-thread implementation.

Key behavior:
- Implements semaphores with a count, `pthread_mutex_t`, and `pthread_cond_t`.
- `wait` blocks while count is zero, then decrements.
- `signal` increments count and signals the condition when transitioning from zero.
- Implements monitors as plain pthread mutexes.
- Creates detached threads by wrapping Ghostscript’s callback signature in a `void *` pthread start routine.
- Maps pthread errors coarsely to `gs_error_ioerror`.

Notable dependencies:
- POSIX pthreads and Ghostscript `gpsync.h`.

Research notes:
- A comment notes error handling should inspect `errno` more precisely.
- The thread wrapper heap-allocates a closure and frees it at thread start.
