# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_turnstile.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_turnstile.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements NetBSD turnstiles: lock wait queues with priority inheritance.

## Purpose And Main Interfaces

- Initialization and construction:
  - `turnstile_init`
  - `turnstile_ctor`
- Lookup and operation control:
  - `turnstile_lookup`
  - `turnstile_exit`
- Blocking and waking:
  - `turnstile_block`
  - `turnstile_wakeup`
- Sleep queue integration:
  - `turnstile_unsleep`
  - `turnstile_changepri`
- Debug support under `LOCKDEBUG`:
  - `turnstile_print`

## Key Data Structures

- `turnstile_chains[128]` maps synchronization object addresses to active turnstiles.
- `turnstile_locks[128]` are cacheline-padded chain locks.
- Each LWP owns a turnstile. A lock object only borrows a turnstile while one or more threads wait on it.
- Active turnstiles contain separate reader and writer sleep queues, wait counts, free turnstile list, object pointer, and priority-inheritance metadata.

## Control Flow

- `turnstile_lookup` hashes the lock object, takes the chain lock, and returns the active turnstile if any. The chain lock remains held.
- `turnstile_exit` releases the chain lock when a caller decides not to block.
- `turnstile_block` either lends the current LWP's turnstile to a lock with no active turnstile or puts the LWP's turnstile on the active turnstile free list. It enqueues the LWP on the selected reader/writer sleep queue, lends priority, then blocks.
- `turnstile_lendpri` walks the blocking chain via syncobj owner callbacks and lends the current effective priority to lower-priority owners to avoid priority inversion.
- `turnstile_unlendpri` removes a turnstile from the inheritor's lender list and recalculates inherited priority.
- `turnstile_wakeup` wakes a specified waiter or the first `count` waiters from the requested queue, restores priority inheritance if needed, removes waiters, and releases the chain lock.
- `turnstile_remove` returns an inactive turnstile to each awakened LWP or removes the active turnstile from the hash when the last waiter leaves.

## Concurrency And Invariants

- Hash chain locks double as sleep queue interlocks.
- Blocking is non-interruptible; `turnstile_unsleep` panics if called.
- Preemption is disabled during the delicate block/priority-lending/sleep sequence.
- The code uses try-lock restart logic while walking owner chains to avoid LWP lock deadlocks.
- Assertions check queue type, waiter counts, active object consistency, and inherited-priority ownership.

## Risks And Edge Cases

- A lock destroyed or corrupted while still in use is likely to trip assertions in priority inheritance paths.
- Priority inheritance is chain-walking and must handle owner changes while locks are dropped.
- `turnstile_changepri` delegates to `sleepq_changepri`; the comment marks priority inheritance handling as incomplete there.
