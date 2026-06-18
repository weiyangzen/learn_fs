# File Research: sources/os/linux/linux-stable/fs/gfs2/glock.h

## Scope

This header declares glock lock types, lock states, lock flags, DLM output flags, lock-module operations, glock-as-address-space wrapper, public glock APIs, debugfs hooks, and small inline helpers.

## APIs And Constants

- Lock types: reserved, nondisk, inode, rgrp, meta, iopen, flock, plock, quota, journal.
- Lock states: unlocked, exclusive, deferred, shared, with comments documenting shared/deferred incompatibility.
- Request flags: try, try-one-callback, recover, any, node-scope, async, exact, skip, no-pid, no-cache, no-block.
- DLM output flags: state mask, try-again, deadlock, canceled, error.
- Hold-time tuning constants for adaptive inode glock caching.
- `struct lm_lockops` defines mount, recovery, unmount, withdraw, put-lock, lock, cancel, and mount-option parsing hooks.
- `gfs2_glock_is_locked_by_me()` scans holders for the current task.
- `gfs2_glock2aspace()` returns the embedded metadata address_space for glops with `GLOF_ASPACE`.
- Declares full glock lifecycle, acquire/release, async wait, callback, delete-work, hash clear, withdraw, thaw, debugfs, object binding, and delete-generation APIs.

## State And Data Structures

- `struct gfs2_glock_aspace` combines a glock and an address_space for inode/meta-style glocks.
- Holder initialization helpers use return addresses for later debug output.
- Inline holder helpers represent initialized and queued state by `gh_gl` and `gh_list`.

## Dependencies

- Includes `incore.h`, so it relies on core GFS2 in-memory structure definitions.
- Consumed across file, inode, rgrp, quota, super, recovery, and metadata paths that acquire cluster locks.

## Risks And Invariants

- Lock flag semantics are part of the glock state machine contract. Misusing `LM_FLAG_ANY`, `GL_EXACT`, or `GL_SKIP` changes correctness of inode instantiation and compatibility.
- `gfs2_glock_is_locked_by_me()` depends on holder owner pids and holder list ordering.
- `gfs2_glock_nq_init()` uninitializes the holder on enqueue failure; callers must not uninit it again unless it succeeded.
