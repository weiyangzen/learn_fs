# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_objset.c

This file implements ZFS DMU objset lifecycle and management: opening, holding, owning, creating, cloning, syncing, evicting, accounting, quota upgrades, statistics, snapshot/child enumeration, and small objset utility helpers.

Core responsibilities:
- Initializes and destroys global objset lock state with `dmu_objset_init()` / `dmu_objset_fini()`.
- Provides accessors for objset SPA, ZIL, DSL pool/dataset, type, name, id, dnode size, sync property, and logbias.
- Registers DSL property callbacks to keep live `objset_t` policy fields synchronized for checksum, compression, copies, dedup, cache policy, sync mode, logbias, redundant metadata, recordsize, dnodesize, and special small-block threshold.
- Opens on-disk `objset_phys_t` through ARC in `dmu_objset_open_impl()`, including encrypted/raw root block handling, block-size expansion for newer `objset_phys_t` layouts, ZIL allocation, special dnode opening, dirty-dnode multilist creation, and mutex setup.
- Converts DSL datasets to objsets with `dmu_objset_from_ds()`, serializing open through `ds_opening_lock`.
- Implements held and owned objset entry points: `dmu_objset_hold_flags()`, `dmu_objset_hold()`, `dmu_objset_own()`, `dmu_objset_own_obj()`, release/disown helpers, and ownership refresh for userspace upgrade flows.
- Handles objset eviction in two phases: unregister properties, tear down SA, evict dbufs, register with SPA eviction tracking, then close special dnodes/free ZIL/ARC buffer/mutexes when all dnodes are gone.
- Creates objsets and datasets via sync tasks: `dmu_objset_create_check()`, `dmu_objset_create_sync()`, and `dmu_objset_create()`. Encrypted creation forces immediate sync of encryption-dependent data before key mapping removal.
- Creates clones from snapshot origins through `dmu_objset_clone_check()`, `dmu_objset_clone_sync()`, and `dmu_objset_clone()`.
- Implements indirect remapping after device removal with `dmu_objset_remap_indirects()`, tracking last remap TXG in the DSL dir.
- Performs objset sync in `dmu_objset_sync()`: writes the root objset block, syncs meta/user/group/project special dnodes, parallel-syncs dirty regular dnodes, handles user accounting lists, updates ZIL header, and starts root block IO.
- Maintains user/group/project space accounting and object accounting through dirty dnode capture, AVL aggregation caches, ZAP increments, and deferred taskq processing.
- Provides upgrade machinery for userspace/userobj/projectquota accounting using `dmu_objset_upgrade()` background task dispatch and stoppable upgrade state.
- Lists snapshots and child dirs through ZAP cursors, and walks whole dataset trees with both path-based and DSL-pool/object based find routines.
- Exposes stats and state helpers such as `dmu_objset_space()`, `dmu_objset_fast_stat()`, `dmu_objset_stats()`, `dmu_objset_is_snapshot()`, encryption compatibility, user pointer accessors, `dmu_fsname()`, and dirty-space reservation.

Important control-flow notes:
- `dmu_objset_open_impl()` is the central constructor for in-memory `objset_t`; it wires together ARC, DSL properties, ZIL, special dnodes, dirty lists, and locks.
- `dmu_objset_sync()` is the central writeback path and assumes syncing context. It uses root block callbacks `dmu_objset_write_ready()` and `dmu_objset_write_done()` to update fill counts, root block pointers, and dataset block accounting.
- User accounting is skipped during encrypted receives and pool claiming, then completed later when keys/ownership make it safe.
- Raw receive state affects objset sync: encrypted objsets can write `os_phys_buf` raw when `os_raw_receive` or `os_next_write_raw` is set.
- `dmu_objset_find_dp()` can parallelize child enumeration with a taskq, unless serialization is requested or the pool config lock is write-held.
- Hidden `$` objsets are deliberately skipped during enumeration.

Key dependencies:
- DSL dataset/dir/pool APIs for ownership, creation, cloning, snapshotting, stats, and namespace traversal.
- ARC/dbuf/dnode/ZIL code for physical IO, dirty tracking, special dnodes, and intent-log syncing.
- ZAP for user accounting objects, snapshot/child listings, and upgrade metadata.
- SPA feature/version checks for userspace accounting, project quota, large dnodes, encryption, and remapping behavior.

Risk-sensitive invariants:
- Many paths require pool config lock or syncing context; assertions encode those contracts.
- Encrypted objset creation and raw receive handling are carefully ordered around key mappings and raw ARC buffers.
- Object accounting relies on dirty dnode ordering and per-TXG dirty links.
- Eviction uses `os_lock` as a barrier for `dnode_move()` safety.
