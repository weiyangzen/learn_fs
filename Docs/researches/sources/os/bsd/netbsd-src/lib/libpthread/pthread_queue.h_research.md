# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_queue.h

This header defines the private `PTQ` intrusive queue macro family used throughout libpthread. It is modeled after BSD tail queues but designed for static initializability. It provides head and entry declarations, initializers, insert-at-head/tail/after/before, removal, empty/first/next/last/prev accessors, and forward/reverse iteration.

The key implementation detail is `ptqh_last`, which may be `NULL` in static initializers and is repaired by `PTQ_INSERT_TAIL` before first insertion. This supports objects like statically initialized synchronization primitives.

Integration points: used for thread cleanup stacks, barrier waiters, rwlock wait queues, all-thread lists, and TSD key lists. Risks are typical intrusive-macro hazards: double insertion/removal, stale prev pointers, and lack of type safety.
