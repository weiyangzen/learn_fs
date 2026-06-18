# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_lock.c

## Purpose
Implements FreeBSD `lockmgr` locks: sleepable shared/exclusive/upgradable locks used heavily by vnode and buffer code.

## Key Interfaces
- Initialization and teardown: `lockinit()`, `lockdestroy()`.
- Policy mutation: `lockallowshare()`, `lockdisableshare()`, `lockallowrecurse()`, `lockdisablerecurse()`.
- Fast entry points: `lockmgr_slock()`, `lockmgr_xlock()`, `lockmgr_unlock()`.
- General entry point: `lockmgr_lock_flags()` and `__lockmgr_args()`.
- State helpers: `_lockmgr_disown()`, `lockmgr_printinfo()`, `lockstatus()`, `_lockmgr_assert()`.
- DDB support: `lockmgr_chain()` and `db_show_lockmgr()`.

## State And Locking
The lock word encodes unlocked, shared count, exclusive owner, waiters, spinners, recursed writer, and disowned `LK_KERNPROC` state. Sleep queues have separate shared and exclusive queues. Thread counters track total locks and shared lockmgr locks. Optional DEBUG_LOCKS stores a stack.

## Control Flow
Shared and exclusive acquisition first try atomic fast paths. Hard paths perform WITNESS order checks, optional adaptive spinning on running exclusive owners, waiters-bit setup, sleepqueue sleeps with timeout/signal handling, Giant save/restore, lock profiling, lockstat probes, and PMC soft events. Release paths prefer exclusive waiters, handle `LK_SLEEPFAIL`, broadcast the selected queue, and preserve waiter bits when required. Upgrade, try-upgrade, downgrade, drain, recurse, and disown are handled as explicit state transitions.

## Integration Notes
Defines `lock_class_lockmgr` for the kernel lock class system, but generic sleep interlocking methods intentionally panic because lockmgr has specialized entry points.

## Risks
This is a delicate atomic state machine. Correctness depends on preserving waiter bits, synchronizing with sleepqueue locks, and maintaining priority rules between exclusive and shared waiters. Recursing non-recursive locks, draining while held, or downgrading recursed locks panics.
