# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_mutex.c

## Purpose
Implements NetBSD kernel mutexes, including adaptive sleepable mutexes, spin mutexes, lockdebug integration, lockstat probes, turnstile blocking/wakeup, priority-inheritance owner lookup, and architecture fast-path aliases.

## Main Interfaces
- `_mutex_init`, `mutex_init`, `mutex_destroy`: initialize/destroy adaptive or spin mutexes based on IPL and debug mode.
- `mutex_vector_enter`, `mutex_vector_exit`: generic enter/exit routines for all mutex types.
- `mutex_tryenter`, `mutex_owned`, `mutex_ownable`.
- `mutex_spin_retry`: retry path for spin mutex stubs.
- `mutex_wakeup`: available on non-simple-mutex architectures.

## Internal State And Dependencies
- Defines `mutex_spin_lockops`, `mutex_adaptive_lockops`, and `mutex_syncobj`.
- Uses architecture lock primitives, atomic CAS/store, memory barriers, SPL raise/restore, `curlwp`, preemption controls, turnstiles, sleep queues, pserialize diagnostics, lockdebug, and lockstat.
- `MUTEX_BIT_SPIN`, `MUTEX_BIT_WAITERS`, `MUTEX_BIT_NODEBUG`, and owner pointer bits encode lock state.

## Control Flow Notes
- Spin mutex enter raises SPL and either takes the simple lock or spins with backoff under MP/debug builds.
- Adaptive mutex enter first tries CAS acquisition. If owned by a running LWP on another CPU, it spins briefly; otherwise it marks waiters under the turnstile chain lock and blocks.
- Adaptive exit can release without interlocked operations when no waiters are observed; otherwise it uses turnstile lookup and wakes all writer waiters.
- `mutex_oncpu` checks whether the owner LWP is currently running, with special handling for kernel big-lock waiters.

## Locking And Memory Ordering
- The file contains extensive comments about races between setting waiters and unlocked `mutex_exit`.
- Acquire/release barriers protect owner publication and release.
- `mutex_oncpu` safety relies on disabled kernel preemption and LWP memory not being returned before pserialize barriers in LWP teardown.
- Spin mutex SPL nesting is tracked in per-CPU `ci_mtx_count` and `ci_mtx_oldspl`.

## Risk Areas
- Adaptive mutex correctness depends on subtle waiter-bit, turnstile, and owner-running checks.
- Recursive adaptive acquisition panics; spin self-locking panics in non-MP/full paths.
- Destroy requires no owner/waiters or no held spin bit.
- Releasing adaptive mutexes before interrupts are initialized has a special `cold` path on architectures without stubs.

## Filesystem Relevance
Foundational. VFS, vnode, buffer cache, and filesystem code rely on these mutex semantics for correctness under SMP and interrupt contexts.
