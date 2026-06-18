# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_turnstile.c

## Purpose
Implements turnstiles: wait queues for non-sleepable locks with priority inheritance. Turnstiles are assigned dynamically to locks via a hash table instead of being embedded in every lock.

## Core Model
- Each thread owns a preallocated turnstile (`td_turnstile`).
- The first waiter lends its turnstile to the contended lock.
- Later waiters put their own turnstiles on the lock turnstile’s free list.
- Woken threads reclaim a turnstile from the lock’s free list or the lock turnstile itself.
- Turnstiles maintain separate exclusive/shared blocked queues plus a pending wake queue.

## Main Structures
- `struct turnstile` contains a spin lock, blocked queues, pending queue, hash/free/list links, referenced lock object, and owner thread.
- `struct turnstile_chain` is a hash bucket protected by a spin mutex.
- `td_contested_lock` protects per-thread lists of contested locks.

## Initialization
- `init_turnstiles()` initializes the chain table, contested lock, and thread0 contested list very early.
- `init_turnstile0()` creates the UMA zone and gives thread0 a turnstile.
- Optional `TURNSTILE_PROFILING` sysctls track chain depth and max depth.

## Waiting and Priority Propagation
- `turnstile_trywait()` locks the chain, finds or prepares a turnstile for a lock.
- `turnstile_wait()` inserts the current thread into the correct shared/exclusive priority queue, lends or free-lists turnstiles, sets thread blocked state, unlocks the chain, propagates priority, emits sleep probe, and context-switches.
- `propagate_priority()` walks owner chains, lending priority through nested lock dependencies. It panics if a sleeping thread owns a non-sleepable lock.
- `turnstile_adjust()` and `turnstile_adjust_thread()` reposition waiters when priority changes and propagate lowered effective priority when needed.

## Ownership and Wakeup
- `turnstile_claim()` gives ownership of a turnstile to the current thread and lends priority from the first waiter.
- `turnstile_signal()` moves the highest-priority waiter in one queue to pending and assigns it a turnstile.
- `turnstile_broadcast()` moves all waiters in one queue to pending and assigns each a turnstile.
- `turnstile_unpend()` clears ownership, recalculates current thread’s lent priority, marks pending threads runnable, clears their blocked state, and releases the turnstile lock.
- `turnstile_disown()` removes ownership without waking, then recomputes current thread priority.

## Lookup and Locking APIs
- `turnstile_chain_lock()`/`turnstile_chain_unlock()` lock hash buckets.
- `turnstile_lookup()` locates and locks a turnstile for a lock under chain lock.
- `turnstile_lock()` safely locks a turnstile from a turnstile pointer if its lock object is stable.
- `turnstile_unlock()` and `turnstile_cancel()` release locks and clear stale current-thread lock object state.
- `turnstile_head()` and `turnstile_empty()` inspect waiter queues.

## Debugging
DDB commands show:
- a turnstile by lock/turnstile address,
- lock chains,
- all chains,
- lock trees/waiter trees.

## Concurrency and Invariants
- Chain spin locks protect hash membership.
- Turnstile spin locks protect blocked/pending queues and owner-sensitive state.
- `td_contested_lock` protects per-thread contested-lock lists.
- Thread lock pointer is switched to the turnstile lock while the thread is blocked.
- Priority queues are ordered by effective priority.

## Filesystem Relevance
Filesystem code frequently uses mutexes/rwlocks around vnode, mount, buffer, and device state. Turnstiles provide priority inheritance for non-sleepable lock contention that can occur on those paths.
