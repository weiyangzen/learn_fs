# File Research: sources/local-fs/btrfs-linux/fs/btrfs/qgroup.h

This header defines Btrfs qgroup data structures, reservation types, runtime flags, mode enum, simple-quota delta structure, and the public API implemented by `qgroup.c`.

Conceptual overview:
- The header documents qgroups in three phases:
  - reserve: pre-account metadata/data space for limit enforcement;
  - trace: record dirty extents whose ownership/reference state may change;
  - account: update qgroup numbers during rescan or transaction commit.
- It also documents the balance relocation optimization using delayed subtree tracing through swapped block records.

Runtime flags:
- `BTRFS_QGROUP_RUNTIME_FLAG_CANCEL_RESCAN` cancels a running rescan.
- `BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING` suppresses live accounting when qgroups are inconsistent or disabled for accounting.
- These share the status-item flags field but count down from the MSB to avoid collision with persisted flags.

Core structures:
- `struct btrfs_qgroup_extent_record` records a dirty extent’s length, old roots, and data reservation bytes/refroot to free at commit.
- `struct btrfs_qgroup_swapped_block` records delayed tracing state for a swapped relocation/subvolume subtree pair.
- `enum btrfs_qgroup_rsv_type` distinguishes data, per-transaction metadata, and preallocated metadata reservations.
- `struct btrfs_qgroup_rsv` stores per-type reserved byte counters.
- `struct btrfs_qgroup` stores usage counters, limits, reservation counters, relation lists, dirty/iterator lists, temporary old/new refcounts, rb-tree node, and sysfs kobject.
- `struct btrfs_qgroup_list` links a member qgroup to a parent qgroup.
- `struct btrfs_squota_delta` describes a simple-quota byte delta by root, length, generation, direction, and data/metadata kind.

Helpers and enums:
- `btrfs_qgroup_subvolid()` extracts the low bits of a qgroup ID.
- Event trace enum values identify reserve, release, and free operations.
- `enum btrfs_qgroup_mode` exposes disabled, full, and simple modes.

Public API groups:
- Mode/status: `btrfs_qgroup_mode()`, `btrfs_qgroup_enabled()`, `btrfs_qgroup_full_accounting()`.
- Quota lifecycle: enable, disable, rescan, resume, wait, read/free config.
- Qgroup graph: add/delete relation, create/remove qgroup, cleanup dropped subvolume, limit qgroup.
- Full accounting trace/account: trace extents, leaves, subtrees, account extents, run qgroups.
- Inherit validation/application: `btrfs_qgroup_check_inherit()` and `btrfs_qgroup_inherit()`.
- Reservation API: data reserve/release/free, metadata prealloc reserve/free, pertrans free, meta conversion, leak check.
- Relocation swap API: init/clean swapped blocks, add swapped records, trace after COW.
- Cleanup/simple quota: destroy extent records and record simple-quota deltas.

Role:
- Serves as the cross-subsystem contract for inode IO, transaction commit, relocation, subvolume creation/deletion, ioctl quota control, and sysfs qgroup exposure.
