# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rwlock.c

## Purpose

Full kernel readers/writer lock implementation with direct turnstile handoff, priority-aware wakeup policy, lockstat probes, panic diagnostics, try/upgrade/downgrade operations, and ownership introspection.

## Lock Representation

The lock is a single machine word containing reader hold count or writer owner pointer plus three low bits: waiters, writer wanted, and write locked. Readers increment by `RW_READ_LOCK`; writers store `curthread | RW_WRITE_LOCKED`.

## Wakeup Policy

- Blocking threads wait on turnstile reader or writer queues.
- Waiters wake already owning the lock by direct handoff.
- Exiting readers grant the lock to waiting writers to avoid writer starvation.
- Exiting writers grant to readers with priority at least that of the highest-priority blocked writer, otherwise to a writer.
- `RW_READER_STARVEWRITER` allows readers to ignore writer-wanted state for acquisition, supporting lock-ordering cases that would otherwise deadlock.

## Key Interfaces

- `rw_init()` and `rw_destroy()` initialize/destroy the word and detect double destroy or active destroy.
- `rw_enter_sleep()` handles contended acquisitions for reader, writer, and starve-writer reader modes.
- `rw_exit_wakeup()` handles final release, turnstile wakeup, and handoff.
- `rw_tryenter()` implements nonblocking read/write acquisition.
- `rw_downgrade()` converts writer ownership to reader ownership and may wake compatible readers.
- `rw_tryupgrade()` converts a sole reader to writer when no other readers/writers block it.
- `rw_read_held()`, `rw_write_held()`, `rw_lock_held()`, `rw_read_locked()`, `rw_iswriter()`, and `rw_owner()` expose state tests.

## Locking and Memory Ordering

- All state changes use atomic compare/add operations except state transfer while holding the turnstile lock.
- `membar_enter()` and `membar_exit()` bracket acquisition/release.
- Waiter and writer-wanted bits are modified under `turnstile_lookup()` to keep turnstile and lock state coherent.
- Optional `rw_lock_backoff` and `rw_lock_delay` hooks support spin backoff under CAS contention.

## Dependencies

Uses turnstiles, sleep object ops, dispatcher priorities, CPU stats, lockstat, atomic primitives, and thread pointers encoded in the lock word.

## Notes for Future Work

- Recursive read acquisition can deadlock when a writer arrives between acquisitions; the file documents this as a semantic consequence of writer-starvation prevention.
- Panic diagnostics save the offending lock address and word before panicking.
