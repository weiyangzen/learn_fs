# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/rw_spinlock.hpp

Purpose: Implements a compact reader-writer spinlock for FOA concurrent containers and stats.

Important APIs, types, and functions: Class `rw_spinlock` provides `try_lock_shared`, `lock_shared`, `unlock_shared`, `try_lock`, `lock`, and `unlock`.

Control flow: A 32-bit atomic state uses bit 31 for exclusive lock, bit 30 for writer pending, and low 30 bits for reader count. Shared lock succeeds only when no writer/exclusive bit is present. Exclusive lock waits until no readers or writer, setting writer-pending when readers are active. The spin loop uses pause, yield, and eventual sleep through Boost.Core yield primitives.

State and persistence behavior: Holds only atomic lock state. No ownership tracking or recursion state exists.

Dependencies and integration points: Used by per-group concurrent table locks, striped container locks, and concurrent stats. Depends on `<atomic>`, `<cstdint>`, and Boost.Core yield primitives.

Risks: Non-reentrant and unfairness is possible under high contention despite writer-pending mitigation. Mispaired unlock calls are undefined by contract. Spinlocks are sensitive to oversubscription.

Test signals: Threaded tests should cover multiple readers, writer exclusion, try-lock behavior, contention progress, and sanitizer runs.
