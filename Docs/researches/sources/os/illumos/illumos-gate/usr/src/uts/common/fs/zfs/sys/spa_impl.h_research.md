# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_impl.h

This private header defines internal SPA structures: error entries, history records, vdev-removal and indirect-condensing physical records, aux-vdev sets, config locks, taskq state, import config sources, and the full `struct spa`.

Core definitions:
- `spa_error_entry_t` stores error bookmarks, object names, and AVL linkage.
- `spa_history_phys_t` tracks persistent history log offsets and lost-record count.
- `spa_removing_phys_t` is persistent pool-removal progress: state, removing/previous indirect vdev IDs, start/end time, bytes to copy, and bytes copied/freed.
- `spa_condensing_indirect_phys_t` persists an in-progress indirect-vdev mapping condense operation.
- `spa_aux_vdev` caches spare/L2ARC config, active vdevs, pending additions, and sync state.
- `spa_config_lock_t` combines mutex, writer pointer, wanted count, CV, and debug refcount.
- `spa_taskqs_t`, `zio_taskq_type_t`, `spa_proc_state_t`, `spa_avz_action_t`, and `spa_config_source_t` define internal scheduling, per-pool process, all-vdev-ZAP, and import-source state.

`struct spa` responsibilities:
- Namespace/config/load state, taskqs, DSL pool, allocation classes, txg/vdev dirty lists, root vdev, ashift bounds, GUIDs, config dirtiness, allocator locks/trees.
- Aux devices, labels/features, MOS objects, checksum salt/templates, uberblocks, scrub/resilver, async tasks, missing-vdev import policy.
- Vdev removal, indirect condensing, checkpoints, log spacemap tracking, error logs, history, properties, pool I/O roots, suspension, claiming, log state, DDT, dedup defaults, feature objects/cache, deadman, all-vdev-ZAP, autotrim, keystore, kstats, MMP, leaf list, and waiters.
- `spa_refcount` and `spa_config_lock[]` are intentionally last for MDB layout compatibility.

Risk-sensitive invariants:
- Many fields are protected by different locks named in comments; callers must follow the matching lock domain.
- Persistent physical structs must remain byteswappable and format-compatible.
- Import/load, sync, removal, checkpoint, log-spacemap, MMP, and suspend state all coexist in one SPA object, so state transitions must avoid cross-subsystem races.
