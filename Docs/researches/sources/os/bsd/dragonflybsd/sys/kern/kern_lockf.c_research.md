# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_lockf.c

## Purpose

`kern_lockf.c` implements advisory byte-range file locking for `fcntl`/`lockf` style POSIX locks and flock-style locks. It manages sorted locked ranges, blocked waiters, deadlock checks, per-UID POSIX lock accounting, and range structure caching.

## Main Responsibilities

- Converts `struct flock` requests into absolute `[start, end]` byte ranges.
- Implements `F_SETLK`, `F_UNLCK`, and `F_GETLK` through `lf_advlock()`.
- Adds, removes, clips, splits, merges, and downgrades lock ranges in `lf_setlock()`.
- Finds conflicting lock holders for `F_GETLK` through `lf_getlock()`.
- Sleeps and wakes blocked lock requests.
- Enforces `RLIMIT_POSIXLOCKS` and `maxposixlocksperuid` for POSIX locks.
- Provides a small two-entry per-CPU cache for `struct lockf_range`.

## Core Data Model

Each `struct lockf` lazily initializes two TAILQs: `lf_range` for active ranges sorted by `lf_start`, and `lf_blocked` for blocked waiters. Each `lockf_range` records owner process, lock type, flags, start, and end. `F_NOEND` represents open-ended locks by using `LLONG_MAX` internally.

The lock object is serialized by an LWKT pool token selected from the `struct lockf *`. This allows the code to modify range lists without per-list locks while still blocking safely.

## Lock Mutation Behavior

`lf_setlock()` preallocates two range objects before editing so it does not have to block mid-mutation. It scans active ranges to find the insertion point, overlapping ranges owned by the caller, and conflicting ranges owned by others. Conflicts either return `EAGAIN`, detect a simple POSIX deadlock as `EDEADLK`, or enqueue a blocked range and sleep.

When no owned overlapping range exists, new locks are inserted directly. Otherwise the function may insert a new requested range, split an existing owned range into two pieces, clip left or right edges, delete enclosed ranges into a temporary dead list, and merge adjacent same-owner same-type ranges. POSIX lock accounting is adjusted before mutation for worst-case growth and corrected after merge/delete.

## Wakeup and Accounting

Unlocks and write-to-read downgrades mark wakeups needed. `lf_wakeup()` scans blocked ranges and wakes all overlapping waiters, marking their `lf_flags` so sleepers know they were removed from the blocked list.

Per-UID accounting uses per-CPU deltas on both `uidinfo` and process-local UID counters. `lf_count_adjust()` moves process lock accounting when credentials change, while `lf_count_change()` checks limits for non-root users and updates counters.
