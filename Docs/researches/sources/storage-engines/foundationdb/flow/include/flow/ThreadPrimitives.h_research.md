<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ThreadPrimitives.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ThreadPrimitives.h

Purpose: This header defines low-level thread synchronization primitives used by Flow's thread-safe utilities. It provides cache-line-aligned spin locks, a one-shot event, and a recursive process-local mutex wrapper.

Important APIs and types: `ThreadSpinLock` exposes `enter`, `leave`, and `assertNotEntered`. `ThreadSpinLockHolder` is an RAII holder. `ThreadUnsafeSpinLock` and holder are no-op variants selected when `FLOW_THREAD_SAFE` is false. `Event` wraps a `std::latch` with `set` and `block`. `Mutex` and `MutexHolder` wrap platform-specific recursive locks.

Control flow: `ThreadSpinLock::enter` spins on an atomic flag with architecture-specific pause instructions. `leave` clears the flag. `SpinLock` aliases either the real spin lock or the no-op version based on `FLOW_THREAD_SAFE`. `Event::block` waits until `set` counts down the latch.

State and persistence behavior: Synchronization state is purely in-memory. The spin lock is padded to `MAX_CACHE_LINE_SIZE` to avoid false sharing. No persistence exists.

Dependencies and integration points: It depends on atomics, latch, platform semaphores or Mach headers, Flow errors and trace, and Valgrind DRD annotations. It underpins `ThreadHelper.actor.h`, `ThreadSafeQueue`, side-thread coordination, and platform thread code.

Risks: Spin locks can waste CPU under long holds and must not protect blocking operations. The no-op alias under `FLOW_THREAD_SAFE == 0` is safe only when caller invariants guarantee single-thread access. `Event` is one-shot because `std::latch` cannot be reset. Platform mutex implementation is hidden behind `void*`.

Test signals: Tests should cover lock exclusion under contention, RAII release, `assertNotEntered`, one-shot event block/unblock, mutex recursion, and Valgrind/TSAN cleanliness where supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ThreadPrimitives.h -->
