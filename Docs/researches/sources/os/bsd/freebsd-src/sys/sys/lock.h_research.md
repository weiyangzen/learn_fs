# File Research: sources/os/bsd/freebsd-src/sys/sys/lock.h

Defines the generic lock-class framework, lock object flags, WITNESS hooks, KTR lock tracing helpers, and adaptive spin delay support.

Key content:
- `struct lock_class` abstracts common operations for lock types: assert, DDB show, lock/unlock around sleep queues, owner query, and trylock.
- Class flags distinguish sleep locks, spin locks, sleepability, recursion, and upgradability.
- Lock object flags cover initialization, WITNESS monitoring, quiet mode, recursion, sleepability, vnode-lock hints, profiling disable, and class index encoding.
- Lock operation flags include trylock, exclusive, duplicate-ok, no-sleep, new-order, and quiet behavior.
- Assertion flags define unlocked, locked, shared, exclusive, recursed, and non-recursed states.
- Kernel-only tracing macros emit KTR lock events when `LOCK_DEBUG > 0`.
- Declares global lock classes for mutex, sx, rw, rm, and lockmgr.
- Provides `lock_delay_*` adaptive spin delay structs and helpers.
- Declares the WITNESS API and maps it to no-op macros when `WITNESS` is disabled.

Research relevance:
- This is the common lock instrumentation layer used by VFS, mount, vnode, mbuf, allocator, and module subsystems.
- `lockmgr.h`, `mount.h`, and `msgbuf.h` depend on lock object/class semantics from this header.
- WITNESS and KTR are essential for diagnosing filesystem locking order and sleep-with-lock bugs.

Cautions:
- Lock class indices are encoded into `lo_flags`, so class mask/shift values are ABI-sensitive inside the kernel.
- Many macros depend on `_KERNEL` and debug config options.
