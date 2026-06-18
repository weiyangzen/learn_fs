# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ioctl.c

## Purpose
Implements the kernel-side HAMMER ioctl dispatcher and local handlers for history, sync TIDs, versioning, filesystem info, snapshots, cleanup config records, and raw data lookup.

## Key Elements
- `hammer_ioctl()` wraps each request in a HAMMER transaction and dispatches by `HAMMERIOC_*` command.
- Mutating commands check read-only state and privilege status before invoking prune, reblock, rebalance, PFS, mirror-write, version-set, volume, snapshot, config-set, and dedup operations.
- Delegates major maintenance operations to other modules: prune, reblock, rebalance, PFS management, mirroring, volume add/delete/list, and dedup.
- `hammer_ioc_gethistory()` scans B-tree records for create/delete TIDs over inode or key-specific history ranges.
- `hammer_ioc_synctid()` triggers no-op, async, single-sync, or double-sync flusher behavior and reports a synchronization TID.
- `hammer_ioc_get_version()` reports supported HAMMER volume versions and descriptions; `hammer_ioc_set_version()` upgrades/downgrades permitted versions and updates the root volume header.
- Snapshot handlers add, delete, and enumerate per-PFS snapshot records under `snapshot_lock`.
- Config handlers read or replace the per-PFS cleanup configuration record.
- `hammer_ioc_get_data()` looks up a supplied B-tree key, extracts leaf/data, and copies bounded data to userland.

## Dependencies
Uses HAMMER transaction, cursor, B-tree, snapshot, flusher, PFS, volume, reblock/rebalance/prune, dedup, and volume-header APIs exposed through `hammer.h`.

## Behavior/Risks
Several ioctl handlers return `0` while placing operation status in `head.error`, matching ioctl continuation semantics. Snapshot/config updates retry on `EDEADLK`. Version changes are guarded but can trigger structural migration such as undo FIFO upgrade. History logic special-cases regular file data keys because HAMMER stores data record keys as `base + length`.
