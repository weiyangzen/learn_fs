# File Research: sources/os/linux/linux-stable/fs/btrfs/qgroup.h

This header defines Btrfs qgroup data structures, reservation types, mode enum, runtime flags, and exported qgroup APIs.

Conceptual overview in comments:
- Qgroups are split into reserve, trace, and account phases.
- Reserve controls quota limit behavior for incoming data/metadata operations.
- Trace records dirty extents that may affect accounting.
- Account updates qgroup counters, normally during transaction commit or rescan.
- A detailed comment describes delayed subtree tracing for balance/relocation swaps, avoiding full subtree scans unless a swapped subtree is later COWed.

Runtime flags:
- `BTRFS_QGROUP_RUNTIME_FLAG_CANCEL_RESCAN`
- `BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING`
These share the status item flags field but count down from the high bits to avoid persisted flag collisions.

Core structs:
- `struct btrfs_qgroup_extent_record` records dirty extent length, data reservation info, and old roots for commit-time accounting.
- `struct btrfs_qgroup_swapped_block` records delayed relocation/swap accounting metadata.
- `enum btrfs_qgroup_rsv_type` defines data, metadata per-transaction, and metadata prealloc reservation buckets.
- `struct btrfs_qgroup_rsv` stores reservation bytes per type.
- `struct btrfs_qgroup` stores accounting counters, limits, reservation state, relation lists, dirty/iterator nodes, temporary refcount fields, rb-tree node, and sysfs kobject.
- `struct btrfs_qgroup_list` links member qgroups to parent qgroups.
- `struct btrfs_squota_delta` represents a simple quota usage/free delta.
- `enum btrfs_qgroup_mode` defines disabled, full, and simple modes.

Public API groups:
- Mode and lifecycle: `btrfs_qgroup_mode()`, `btrfs_qgroup_enabled()`, `btrfs_qgroup_full_accounting()`, quota enable/disable, config read/free.
- Rescan: start, resume, wait for completion.
- Hierarchy: add/delete relation, create/remove qgroup, cleanup dropped subvolume, limit qgroup.
- Full accounting trace/account: trace extent, trace leaf items, trace subtree, account extent(s), run dirty qgroups.
- Inheritance: check inherit structure and apply qgroup inheritance.
- Reservations: data reserve/release/free, metadata prealloc reserve/free, per-transaction metadata free, metadata conversion, leak checks.
- Relocation/swap: init/clean/add swapped blocks, trace subtree after COW, destroy extent records.
- Simple quota: `btrfs_record_squota_delta()`.

Role in the subsystem:
- Defines the qgroup contract used across Btrfs transaction, extent, inode, relocation, ioctl, and sysfs paths.
