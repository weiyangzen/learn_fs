# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_fs.h

Role: Defines OCFS2 on-disk ABI: revisions, feature flags, signatures, limits, system inode names, directory formats, dinodes, allocators, extents, xattrs, refcount trees, quota formats, and size calculation helpers. This file is shared with userspace-aware code paths through `#ifdef __KERNEL__` variants.

Key constants and feature flags:
- Revision level `0.90`.
- Superblock location `OCFS2_SUPER_BLOCK_BLKNO == 2`.
- Cluster limits: 4 KiB to 1 MiB; block limits: 512 bytes to 4 KiB.
- Object signatures for superblock, dinode, extent block, group descriptor, xattr block, directory trailer, dx root/leaf, and refcount block.
- Supported compat/incompat/ro-compat masks.
- Incompat features include local mount, sparse alloc, inline data, userspace stack, extended slot map, xattr, metadata ECC, indexed dirs, refcount tree, discontiguous block groups, clusterinfo, and append DIO.
- Special non-supported mount-blocking flags include heartbeat device, resize in progress, and tunefs in progress.
- Dinode flags cover valid, orphaned, system inode roles, local alloc, bitmap, journal, heartbeat, chain allocator, truncate log, quota, and direct-IO orphan state.
- Dynamic dinode features cover inline data, xattr presence, inline xattrs, indexed directories, and refcounted data.
- Extent flags cover unwritten and refcounted extents.
- Limits include filename length 255, slots 255, UUID length 16, volume label 64, stack label 4, cluster name 16, minimum journal size 4 MiB, and minimum inline xattr size 256.

System inode model:
- Enumerates global system inodes: bad blocks, global inode allocator, slot map, heartbeat, global bitmap, user quota, group quota.
- Enumerates per-slot local system inodes: orphan dir, extent allocator, inode allocator, journal, local alloc, truncate log, local user quota, local group quota.
- `ocfs2_system_inodes[]` maps each type to name format, inode flags, and mode.
- Helpers identify global system inode types and format names with or without slot numbers.

Core on-disk structures:
- `struct ocfs2_block_check`: CRC32/ECC trailer embedded in metadata when meta-ECC is enabled.
- `struct ocfs2_extent_rec`, `ocfs2_extent_list`, and `ocfs2_extent_block`: extent B-tree records and blocks.
- `struct ocfs2_chain_rec`, `ocfs2_chain_list`, `ocfs2_group_desc`: chain allocator and group bitmap metadata, including discontiguous block group support.
- `struct ocfs2_truncate_log` and `ocfs2_truncate_rec`: deferred deallocation log records.
- `struct ocfs2_slot_map`, `ocfs2_extended_slot`, `ocfs2_slot_map_extended`: old and extended cluster slot maps.
- `struct ocfs2_cluster_info`: cluster stack label, stack flags, and cluster name.
- `struct ocfs2_super_block`: superblock payload stored inside a dinode, constrained to fit in the minimum block size.
- `struct ocfs2_local_alloc`: per-slot local allocation bitmap.
- `struct ocfs2_inline_data`: inline file/directory data header.
- `struct ocfs2_dinode`: central inode-on-disk format containing identity, owner, size, mode, link counts, flags, timestamps, xattr/refcount pointers, suballocator location, DIO orphan slot, and unioned payload for superblock, local alloc, chain list, extent list, truncate log, inline data, or symlink bytes.
- `struct ocfs2_dir_entry`, `ocfs2_dir_block_trailer`, `ocfs2_dx_entry`, `ocfs2_dx_entry_list`, `ocfs2_dx_root_block`, `ocfs2_dx_leaf`: unindexed and indexed directory formats.
- `struct ocfs2_refcount_rec`, `ocfs2_refcount_list`, `ocfs2_refcount_block`: reflink/reference count tree format.
- Xattr structures: `ocfs2_xattr_entry`, `ocfs2_xattr_header`, `ocfs2_xattr_value_root`, `ocfs2_xattr_tree_root`, `ocfs2_xattr_block`, with helpers for local/external flag and type packing.
- Quota disk structures: global/local magic/version arrays, quota headers, global info and dquot blocks, local quota info/chunks/dquot deltas, quota block trailer, and trailer-location helper.

Sizing helpers:
- Kernel helpers compute fast symlink payload, inline data size with inline xattrs, extent records per dinode/extent block/group desc/dx root/refcount block, chain records per dinode, dx entries per root/leaf, local allocation bitmap size, group bitmap size, truncate records per inode, backup superblock block numbers, xattr records per block, and refcount records per block.
- Non-kernel variants provide similar calculations using blocksize arguments for userspace tooling.
- `ocfs2_set_de_type()` maps inode mode to directory entry file type.
- `ocfs2_gd_is_discontig()` detects group descriptors whose bitmap area is followed by a nonempty extent list.

Design notes:
- Layout comments include fixed offsets, making this header the canonical disk-format reference.
- The superblock is embedded in a dinode payload and explicitly constrained to fit within a 512-byte minimum block payload.
- Directory indexing, xattrs, refcounting, metadata ECC, append DIO, and discontiguous block groups are all represented as feature-gated disk formats here.
