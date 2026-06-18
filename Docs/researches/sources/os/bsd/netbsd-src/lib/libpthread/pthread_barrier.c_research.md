# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_barrier.c

This file implements POSIX barriers and barrier attributes. `pthread_barrier_init` validates the optional attribute, rejects a zero count, initializes the waiter queue, stores the configured count, and starts generation and current count at zero. `pthread_barrier_destroy` requires a valid barrier with no current waiters and marks it dead.

`pthread_barrier_wait` uses a hash mutex around the barrier object, a generation counter, and a `PTQ` waiter list. The thread that satisfies the barrier advances the generation, resets the count, unparks all waiters, unlocks, and returns `PTHREAD_BARRIER_SERIAL_THREAD`. Other threads enqueue themselves, set `pt_sleepobj`, and park until generation changes. The implementation explicitly notes that barrier wait is not a cancellation point, simplifying wakeup ownership.

Barrier attributes are minimal: init/destroy only manage magic values. If `_PTHREAD_PSHARED` is enabled, process-private is accepted and process-shared returns `ENOSYS`.

Integration points: depends on `pthread__hashlock`, `pthread__park`, `pthread__unpark_all`, and `PTQ` queues. Risks are misuse during destroy while waiters exist and unsupported process-shared semantics.
