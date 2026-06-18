# File Research: sources/os/bsd/freebsd-src/sys/sys/mutex.h

This kernel header defines FreeBSD mutex types, state bits, APIs, fast-path macros, thread lock helpers, mutex pools, Giant handling, and sysinit glue. It includes lock object definitions and, under `_KERNEL`, per-CPU, lock profiling/stat, atomic, and CPU function headers.

Mutex initialization options include `MTX_DEF` sleep mutexes, `MTX_SPIN` spin mutexes, recursion support, WITNESS/profile suppression, and `MTX_NEW`. Runtime state is stored in `mtx_lock`; sleep mutexes use flag bits for recursion, waiters, and destroyed state, while spin locks are handled separately. Public macros intentionally route through members like `mtx_lock` to catch malformed objects at compile time.

The header is performance-critical: non-debug kernels inline common lock/unlock paths using atomic compare-and-swap/fcmpset operations, only falling back to sleep or spin helper functions when profiling is active or the fast path fails. SMP spin lock paths enter critical spinlock state before acquisition and release it on unlock; UP paths maintain recursion directly. Debug/profile configurations route calls through out-of-line wrappers that preserve file/line information.

It also defines `thread_lock`, `thread_unlock`, `mtx_sleep`, ownership/recursion/initialization/name accessors, and mutex pool helpers. `DROP_GIANT`/`PICKUP_GIANT` save and restore Giant recursion around code that must temporarily release it. `MTX_SYSINIT` creates static initializer and uninitializer records. This file is foundational kernel synchronization infrastructure used throughout VFS, VM, device drivers, and networking.
