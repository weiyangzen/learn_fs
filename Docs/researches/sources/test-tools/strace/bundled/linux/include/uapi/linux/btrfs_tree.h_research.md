# sources/test-tools/strace/bundled/linux/include/uapi/linux/btrfs_tree.h

Purpose: defines the exported Btrfs on-disk tree constants and item layouts visible through userspace tooling, especially `BTRFS_IOC_SEARCH_TREE` consumers. In this repository it is a bundled UAPI source for strace-style decoding, so its stable numeric constants, packed structs, and helper macros are the important surface.

Important APIs/types/functions: includes `BTRFS_MAGIC`, tree object IDs, item key type constants, checksum types, file type and inode flag masks, `struct btrfs_disk_key`, `struct btrfs_key`, `struct btrfs_header`, leaf/node item layouts, device/chunk/superblock structures, extent/reference/inode/root/balance/file-extent/qgroup structures, and block-group/profile masks. Inline helpers are `btrfs_dir_flags_to_ftype`, `btrfs_legacy_root_item_size`, `chunk_to_extended`, `extended_to_chunk`, and `btrfs_qgroup_level`.

Control flow: there is no syscall implementation here. The only executable behavior is deterministic bit/offset transformation: directory flags are masked to remove encryption state, root-item legacy size is derived with `offsetof`, chunk profiles gain or drop the synthetic single-allocation bit, and qgroup level is extracted from the upper bits of an ID.

State and persistence behavior: this header describes persistent Btrfs metadata: superblocks, backup roots, btree headers, leaves/nodes, device items, chunks/stripes, free-space records, extent references, inode/root records, balance resume state, device replacement state, block groups, qgroup accounting, verity descriptors, and remap records. Fields are little-endian and packed; layout changes are ABI and disk-format sensitive.

Dependencies: depends on `<linux/btrfs.h>`, `<linux/types.h>`, and `<stddef.h>`. It also assumes Btrfs UUID/stat constants from the broader Btrfs UAPI and uses fixed-width Linux integer aliases plus `__DECLARE_FLEX_ARRAY`.

Integration points: strace and other decoders use the constants to print Btrfs search keys, ioctl payloads, tree item types, flags, and nested item structures. Kernel and btrfs-progs integration depends on preserving numeric key order, packed alignment, reserved values, and obsolete aliases that prevent accidental reuse.

Risks: high risk comes from enum/key drift, reused obsolete values, packed layout mistakes, endian confusion, and treating flexible item payloads as fixed size. `BTRFS_*_KEY` ordering is part of on-disk semantics, not just names. Superblock reserved fields and newer remap/qgroup fields must be decoded defensively because older kernels/filesystems may lack them.

Test signals: good signals are strace decoder tables matching these constants, compile-time size/offset checks against the bundled header, Btrfs ioctl decode tests with search-tree results, and samples containing mixed old/new metadata such as legacy root items, qgroups, free-space-tree entries, and remap items.
