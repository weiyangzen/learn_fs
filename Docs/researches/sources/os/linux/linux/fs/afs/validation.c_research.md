# File Research: sources/os/linux/linux/fs/afs/validation.c

## Scope

This file implements vnode and volume validity checks based on callbacks, callback expiry, RO snapshot changes, VolSync timestamps, and data-version invalidation.

## Public And Internal APIs Covered

- `afs_check_validity()` fast-checks whether a vnode can be used without network validation.
- `afs_update_volume_state()` processes successful operation callback/VolSync state.
- `afs_validate()` performs blocking vnode/volume validation and cache invalidation.

## Control Flow And Behavior

- The header comment defines the validity model: server callback initialization, vnode callbacks for RW data, volume callbacks for RO/backup releases, VolSync creation/update timestamps, and scrub/snapshot counters.
- `afs_check_validity()` rejects vnodes with broken volume counters, missing/expiring vnode or volume callback promises, RO snapshot changes, scrub counter changes, or `AFS_VNODE_ZAP_DATA`.
- VolSync creation changes initialize timestamps, detect RW restore or timestamp regression, advance RO snapshot state on expected releases, and query VLDB/server exclusion state to handle ongoing RO replication.
- VolSync update regressions increment the volume scrub counter.
- `afs_update_volume_state()` records volume/server callback expiry when an operation received callbacks and advances `cb_v_check`.
- `afs_validate()` serializes through `vnode->validate_lock`, optionally takes the volume callback-check mutex, fetches status when callback state is stale, maps `-ENOENT` to deleted/`-ESTALE`, updates vnode snapshot/scrub mirrors, and zaps data or symlink contents when needed.
- Regular-file cache invalidation preserves dirty/locked/mapped/writeback pages where appropriate; directories and symlinks are discarded more aggressively.

## State And Data Structures

- Volume fields include `cb_v_break`, `cb_v_check`, `cb_scrub`, `cb_ro_snapshot`, `cb_expires_at`, `creation_time`, and `update_time`.
- Vnode fields include `cb_expires_at`, `cb_ro_snapshot`, `cb_scrub`, flags, and validation lock.
- Operations provide pre/post VolSync values and returned callback records.

## Dependencies

- File-server status fetch, volume status refresh, callback promise helpers, page-cache invalidation, symlink invalidation, and tracepoints.

## Risks And Invariants

- Callback expiry uses a 10-second deadline margin.
- Volume timestamp updates are serialized by `volsync_lock` to prevent racing operations from fighting.
- RO release handling must distinguish expected snapshot advancement from regression requiring cache scrub.
