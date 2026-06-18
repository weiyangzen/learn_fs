# sources/test-tools/stress-ng/core-lock.c

## Purpose

This file implements stress-ng's shared lock abstraction. It selects one available primitive at compile time, maps a shared lock pool, allocates lock handles from that pool, and exposes generic create/destroy/acquire/release functions.

## Important APIs, Types, And Functions

`stress_lock_u_t` stores the selected primitive: atomic spin flag, pthread spinlock, pthread mutex, C11 `mtx_t`, Linux PI futex, POSIX semaphore, or SysV semaphore. `stress_lock_t` wraps a magic value and the union. `stress_lock_funcs_t` holds method name and function pointers. Public APIs are `stress_lock_mem_map`, `stress_lock_mem_unmap`, `stress_lock_create`, `stress_lock_destroy`, `stress_lock_acquire`, `stress_lock_acquire_relax`, and `stress_lock_release`.

`stress_lock_get` and `stress_lock_put` allocate/free entries from the shared array under `stress_lock_big_lock`. Atomic spinlock acquisition includes optional architecture-specific pause/yield backoff and aborts with `EAGAIN` if the global run has stopped for more than five seconds.

## Control Flow

Compile-time `LOCK_METHOD_*` macros select the first supported implementation through `#if/#elif`. `stress_lock_mem_map` allocates an anonymous shared mapping sized for `STRESS_LOCK_MAX`, names it when possible, initializes slot zero as the big lock, and sets its magic. `stress_lock_create` obtains a free slot and initializes the selected primitive. Destroy deinitializes and returns the slot to the pool. Acquire/release validate magic before dispatching to the selected primitive.

## State And Persistence Behavior

The shared lock pool persists in an anonymous shared mapping across forked processes until `stress_lock_mem_unmap`. Slot magic values track allocation state. SysV semaphore locks may create kernel semaphore IDs that must be removed during deinit. The big lock serializes lock pool allocation and free operations.

## Dependencies And Integration Points

The module depends on architecture pause helpers, pthread/semaphore/futex/C11 thread availability, mmap helpers, memory anon naming, global continue flag, scheduler yield, and logging. The warn-once system and many shared stress-ng structures depend on this lock abstraction.

## Risks And Test Signals

Risks include no available lock primitive, process-shared semantics not actually supported by the selected primitive, deadlocks in the big lock, stale magic after unmap, semaphore leaks, and unfair atomic spin behavior. Test signals include map/unmap lifecycle, create/destroy pool reuse, invalid-handle errors, cross-process lock exclusion, relaxed acquire backoff under contention, and fallback failure when no primitive is compiled.
