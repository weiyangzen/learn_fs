# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_rwlock.c

## Purpose

`kern_rwlock.c` implements NetBSD kernel reader/writer locks. The design is partially adaptive: waiters may spin while a write owner is actively running on a CPU, and otherwise block on turnstiles with priority inheritance support.

## Main Responsibilities

- Implements:
  - `rw_init`
  - `rw_destroy`
  - `rw_vector_enter`
  - `rw_vector_exit`
  - `rw_vector_tryenter`
  - `rw_downgrade`
  - `rw_tryupgrade`
  - diagnostic held-state helpers.
- Integrates with:
  - LOCKDEBUG;
  - LOCKSTAT;
  - turnstiles;
  - sleep queues;
  - priority inheritance via `rw_owner()`.

## Lock Word Model

- `rw->rw_owner` encodes:
  - write owner LWP pointer;
  - reader count;
  - `RW_WRITE_LOCKED`;
  - `RW_HAS_WAITERS`;
  - `RW_WRITE_WANTED`;
  - optional `RW_NODEBUG`.
- Readers acquire by adding `RW_READ_INCR`.
- Writers acquire by adding current LWP pointer plus `RW_WRITE_LOCKED`.
- The implementation uses CAS and swap on the owner word, with acquire/release memory barriers.

## Initialization and Debugging

- `_rw_init()` initializes lock debug state if enabled and otherwise sets `rw_owner` to zero.
- `rw_destroy()` asserts the lock is not held and frees lockdebug metadata.
- `rw_dump()` prints owner/count and flags.
- `rw_abort()` calls `LOCKDEBUG_ABORT()` unless already panicking.

## Adaptive Spinning

- `rw_oncpu()` checks whether the write owner is currently running on a CPU and is not waiting for the big kernel lock.
- `rw_vector_enter()` spins with backoff while the owner is on CPU and there are no effective sleep waiters.
- If spinning no longer applies, the code enters the turnstile path.

## Enter Path

- Readers wait if a writer holds or wants the lock.
- Writers wait if any writer/reader ownership is present.
- On uncontended acquisition:
  - CAS updates owner word;
  - acquire barrier is issued;
  - LOCKDEBUG/LOCKSTAT bookkeeping is completed.
- On contended acquisition:
  - marks waiter bits;
  - blocks on reader or writer turnstile queue;
  - writer may receive direct handoff.

## Exit Path

- `rw_vector_exit()` subtracts the reader or writer acquisition encoding.
- If no waiters or the lock remains held, it CASes and returns.
- If lock becomes free with waiters:
  - obtains turnstile interlock;
  - prefers waking readers after write release when readers are queued;
  - may direct-handoff to the longest-waiting writer;
  - may wake all writers to compete when no readers are queued;
  - blocks new readers with `RW_WRITE_WANTED` when writers remain.

## Try, Downgrade, Upgrade

- `rw_vector_tryenter()` attempts non-blocking acquisition and returns 0 on contention.
- `rw_downgrade()` converts writer hold to reader hold:
  - fast path when no waiters;
  - otherwise wakes blocked readers while preserving writer-wanted state.
- `rw_tryupgrade()` succeeds only when the caller is the sole reader; converts reader count to write ownership.

## Diagnostic Helpers

- `rw_read_held()` reports read-held state for assertions only.
- `rw_write_held()` checks caller write ownership.
- `rw_lock_held()` checks any ownership.
- `rw_lock_op()` returns `RW_READER` or `RW_WRITER` for a lock known to be held.
- `rw_owner()` returns the write owner for priority inheritance, or NULL if not write-held.
