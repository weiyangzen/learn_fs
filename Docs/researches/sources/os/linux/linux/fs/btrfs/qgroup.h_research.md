# File Research: sources/os/linux/linux/fs/btrfs/qgroup.h

This header defines Btrfs quota group public structures, enums, runtime flags, and function prototypes.

Conceptual overview:
- Comments split qgroup behavior into reserve, trace, and account phases.
- A long balance optimization comment explains delayed subtree tracing for relocation swaps.

Important definitions:
- Runtime-only qgroup status flags:
  - `BTRFS_QGROUP_RUNTIME_FLAG_CANCEL_RESCAN`
  - `BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING`
- `BTRFS_QGROUP_DROP_SUBTREE_THRES_DEFAULT` defaults subtree-drop inconsistency threshold to `3`.
- `enum btrfs_qgroup_rsv_type` defines data, per-transaction metadata, and preallocated metadata reservations.
- `enum btrfs_qgroup_mode` defines disabled, full, and simple modes.
- Trace event operation enum covers reserve, release, and free.

Core structs:
- `struct btrfs_qgroup_extent_record` records dirty extent size, old roots, and deferred data-reservation release info.
- `struct btrfs_qgroup_swapped_block` records relocation/subvolume subtree swap metadata for delayed tracing after COW.
- `struct btrfs_qgroup_rsv` stores reservation counters by reservation type.
- `struct btrfs_qgroup` stores qgroup ID, referenced/exclusive counters, compressed counters, limit fields, reservations, relation lists, dirty/iterator links, temporary accounting refcounts, rb-tree node, and sysfs kobject.
- `struct btrfs_qgroup_list` links member and parent qgroups.
- `struct btrfs_squota_delta` describes simple-quota ownership deltas.

Public API categories:
- Mode and lifecycle: `btrfs_qgroup_mode()`, `btrfs_qgroup_enabled()`, `btrfs_quota_enable()`, `btrfs_quota_disable()`.
- Rescan: `btrfs_qgroup_rescan()`, resume, wait, and config loading/freeing.
- Relations and qgroups: add/delete relation, create/remove qgroup, dropped-subvolume cleanup, limit updates.
- Full accounting: trace extents/leaves/subtrees, account extents, run qgroups.
- Inheritance: check and apply qgroup inheritance.
- Reservations: data reserve/release/free, metadata reserve/free/convert, leak checks.
- Relocation swaps: init/clean/add swapped blocks and trace after COW.
- Simple quota: `btrfs_record_squota_delta()`.

Role:
- Shared contract for qgroup code used by transaction, inode, extent, relocation, ioctl, and sysfs paths.
