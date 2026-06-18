# File Research: sources/os/linux/linux/fs/gfs2/glock.h

## Scope

Declares the public glock interface, lock manager state/type/flag constants, lock manager operation vector, glock address-space wrapper, holder helpers, debug/assert macros, and lifecycle APIs used throughout GFS2.

## APIs And Constants

- Lock types: `LM_TYPE_INODE`, `LM_TYPE_RGRP`, `LM_TYPE_META`, `LM_TYPE_IOPEN`, `LM_TYPE_FLOCK`, `LM_TYPE_PLOCK`, `LM_TYPE_QUOTA`, `LM_TYPE_JOURNAL`, and nondisk/reserved types.
- Lock states: `LM_ST_UNLOCKED`, `LM_ST_EXCLUSIVE`, `LM_ST_DEFERRED`, `LM_ST_SHARED`.
- Request flags include try-lock, recovery, any-state, node-scope, async, exact, skip, no-pid, no-cache, and no-block modes.
- DLM reply flags include state mask, retry/deadlock/canceled/error statuses.
- Defines `struct lm_lockops`, the lock manager interface used by `glock.c`.
- Declares holder/glock APIs for get/put, enqueue/dequeue, waits, multi-lock acquisition, callbacks, delete work, hash clear, withdraw, thaw, debugfs, and object association.
- Inline helpers include `gfs2_glock_is_locked_by_me()`, `gfs2_glock2aspace()`, `gfs2_glock_nq_init()`, `gfs2_holder_initialized()`, `gfs2_holder_queued()`, and `glock_needs_demote()`.

## Invariants

- `gfs2_glock_is_locked_by_me()` only scans current granted holders and stops at first waiter.
- `gfs2_glock2aspace()` is valid only for glock operation types with `GLOF_ASPACE`.
- `gfs2_glock_nq_init()` owns cleanup on enqueue failure by uninitializing the holder.
- `GLOCK_BUG_ON` dumps glock state before crashing, making glock invariants diagnosable.
