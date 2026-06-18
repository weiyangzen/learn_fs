# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwstlock.h

## Role

`rwstlock.h` defines an alternate readers-writer lock that is interruptible and may be released by a thread other than the acquiring thread.

## Data Model

`rwstlock_t` contains:
- `rwst_count`: positive reader count, negative writer ownership encoding, or zero.
- reader and writer condition variables.
- mutex.

Writer ownership is encoded with `LONG_MIN | curthread`, and macros can recover the owner by masking off `LONG_MIN`.

## Operations and Macros

Flags:
- `RWST_TRYENTER`
- `RWST_SIG`

Macros test held/read/write ownership, waiters, signal-aware waits, wakeups, and read/write enter/exit count transitions.

The API includes:
- `rwst_enter()`, `rwst_enter_sig()`, `rwst_tryenter()`
- `rwst_exit()`
- `rwst_init()`, `rwst_destroy()`
- `rwst_lock_held()`
- `rwst_owner()`

## Research Notes

Unlike normal rwlocks, this lock is designed for interruptible acquisition and cross-thread release. The encoded owner/count field is the key invariant.
