# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_removal.h

This header declares active vdev removal and indirect-vdev condensing state.

Core definitions:
- `spa_vdev_removal_t` stores removing vdev ID, per-TXG max offset to sync, removal thread, current metaslab allocated segments, lock/CV/exit flag, per-TXG new mapping lists, per-TXG frees intersecting in-flight mappings, per-TXG bytes done, and leaf-ZAP unlink list.
- `spa_condensing_indirect_t` stores per-TXG new mapping entries and the new mapping object during condense.

Public API surface:
- Initialize/restart removal and initialize/finalize/start/suspend indirect condensing.
- Start/cancel/suspend vdev removal, free ranges from the removing vdev, get removal stats, sync removal state, and destroy removal state.
- Tunables `vdev_removal_max_span` and `zfs_remove_max_segment`.

Risk-sensitive invariants:
- New mapping lists and free-range trees are per-TXG because removal updates are synced transactionally.
- Frees racing with copied mappings must be accounted so the removal does not preserve dead data.
- Condensing replaces indirect mapping state and must coordinate with readers via vdev indirect locks.
