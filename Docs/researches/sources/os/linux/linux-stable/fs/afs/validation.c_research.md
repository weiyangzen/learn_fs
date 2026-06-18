# File Research: sources/os/linux/linux-stable/fs/afs/validation.c

## Scope

Implements vnode and volume validity checks using callback promises, volume callbacks, VolSync timestamps, and cache-scrub counters.

## APIs And Behavior

- `afs_check_validity()` performs a lockless validity test against vnode deletion, callback expiry, volume callback break/check counters, RO snapshot counters, scrub counters, and zap flags.
- VolSync helpers update volume creation/update times, detect RO snapshot advance, RW/backup regressions, excluded servers during replication, and scrub-triggering timestamp regressions.
- `afs_update_volume_state()` records callback expiry for server/volume entries and advances `cb_v_check` after successful operations.
- `afs_validate()` serializes validation, optionally locks the volume callback check, fetches status when promises/counters are stale, handles deleted vnodes, updates vnode snapshot/scrub mirrors, invalidates mmaps, zaps regular data, or invalidates symlink content.

## State And Dependencies

Touches `struct afs_vnode`, `struct afs_volume`, server-list callback expiry, vnode/volume callback counters, page cache, mmap mappings, symlink cache, and `afs_fetch_status()`. It depends on callback handling elsewhere to increment break counters.

## Risks And Invariants

Volume-level and vnode-level callback state must be reconciled in order. RO volume snapshot changes should advance `cb_ro_snapshot`, while regressions or unexpected creation-time changes scrub caches. Status fetches are the authoritative repair path when callback promises expire or are broken.
