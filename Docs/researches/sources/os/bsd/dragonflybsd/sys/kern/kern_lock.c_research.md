# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_lock.c

## Purpose

`kern_lock.c` implements DragonFlyBSD's `lockmgr` shared/exclusive lock primitive. The implementation is largely encoded in an atomic `lk_count` word, with explicit support for shared locks, exclusive locks, recursion, upgrade/downgrade, cancellation, sleep interruption, timed waits, and diagnostic status reporting.

## Main Responsibilities

- Acquires shared locks with `lockmgr_shared()`.
- Acquires exclusive locks with `lockmgr_exclusive()`.
- Downgrades exclusive locks to shared with `lockmgr_downgrade()`.
- Upgrades shared locks to exclusive with `lockmgr_upgrade()`.
- Releases locks and grants pending requests with `lockmgr_release()`.
- Starts and ends cancellation of cancelable blocked/future waiters.
- Initializes, reinitializes, uninitializes, queries, and prints lock state.
- Provides SYSINIT support through `lock_sysinit()`.

## Core State Machine

`lk_count` encodes shared-holder count, exclusive-holder count, request bits, upgrade request, cancellation, and shared-grant state. `lk_lockholder` identifies the exclusive holder only; shared ownership is intentionally not tracked per thread. `LKC_EXREQ2` aggregates exclusive waiters that could not set `LKC_EXREQ` immediately and need a wakeup opportunity.

The code keeps shared and exclusive request interactions explicit: exclusive requests block new shared grants while a shared lock exists, upgrade requests have priority over normal exclusive requests in several grant paths, and shared requests can proceed once the `LKC_SHARED` grant bit is set.

## Acquisition and Upgrade Behavior

Shared acquisition permits recursive acquisition by the exclusive owner only if `LK_CANRECURSE` is set. Otherwise it bumps `LKC_SCOUNT`, waits until `LKC_SHARED` is set, and undoes the count on cancellation, nowait failure, or sleep failure.

Exclusive acquisition handles recursive exclusive counts, then either immediately grants the lock or sets `LKC_EXREQ`/`LKC_EXREQ2` and sleeps. If a blocked exclusive request is canceled or interrupted, `undo_exreq()` either removes the request or reports that the lock was granted before the undo completed.

Upgrade attempts immediately succeed when the caller is the only shared holder. Otherwise the caller drops its shared count and sets `LKC_UPREQ`. If another upgrade exists, non-exclusive upgrade falls back to release-plus-exclusive-acquire, while `LK_EXCLUPGRADE` and `LK_NOWAIT` fail.

## Release and Cancellation

`lockmgr_release()` never blocks. On last exclusive or shared release it grants pending upgrade or exclusive requests by transferring the final count into an exclusive count and waking the requester. Otherwise it clears counts, preconditions the unlocked state for shared acquisition, or delegates shared-count race handling to `undo_shreq()`.

`lockmgr_cancel_beg()` sets `LKC_CANCEL` while the lock is held and wakes pending waiters; only callers using `LK_CANCELABLE` observe cancellation as `ENOLCK`. `lockmgr_cancel_end()` clears the cancel bit.

## Safety and Diagnostics

`_lockmgr_assert()` panics if a potentially blocking operation is attempted from interrupt/IPI/hard code context. `lockstatus()`, `lockowned()`, and `lockmgr_printinfo()` provide caller-visible status. `lockuninit()` asserts no request bits remain and the shared state is consistent.
