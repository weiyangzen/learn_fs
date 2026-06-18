# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_fs.h

Purpose: defines OCFS2's on-disk ABI: revision numbers, feature flags, object signatures, inode/superblock/extent/directory/allocator/refcount/xattr/quota structures, system inode names, layout-capacity helpers, and directory/type utilities shared by kernel and userspace.

Read coverage: complete file read, 1,616 lines.

Format constants and features:
- Defines OCFS2 revision `0.90`, superblock block number 2, cluster/block size limits, object signatures for superblock/dinode/extent/group/xattr/dir trailer/dx root/dx leaf/refcount block, and supported compat/incompat/ro-compat masks.
- Incompat features include local mount, sparse allocation, inline data, extended slot map, userspace stack, xattrs, indexed dirs, metadata ECC, refcount tree, discontiguous block groups, clusterinfo, and append DIO. Heartbeat-only and resize/tunefs-in-progress bits are intentionally not mount-supported in the same way.
- Defines dinode flags such as valid, orphaned, system, superblock, local alloc, bitmap, journal, heartbeat, chain, dealloc, quota, and DIO orphaned.
- Defines dynamic inode features for inline data, xattrs, indexed dirs, and refcount-tree attachment.
- Maps user-visible inode attributes to Linux `FS_*` flags and defines extent flags for unwritten and refcounted extents.

System files and names:
- Enumerates global and slot-local system inode types: bad block, global inode alloc, slot map, heartbeat, global bitmap, global quotas, orphan dir, extent alloc, inode alloc, journal, local alloc, truncate log, and local quota files.
- `ocfs2_system_inodes[]` defines each system inode name template, required dinode flags, and file mode.
- `ocfs2_system_inode_is_global()` and `ocfs2_sprintf_system_inode_name()` distinguish single-copy system inodes from per-slot inodes.

Major on-disk structures:
- `struct ocfs2_block_check` stores metadata CRC/ECC trailers.
- `struct ocfs2_extent_rec`, `ocfs2_extent_list`, `ocfs2_extent_block` define extent trees.
- `struct ocfs2_chain_rec`, `ocfs2_chain_list`, and `ocfs2_group_desc` define allocation chains and bitmap groups, including discontiguous block-group support.
- `struct ocfs2_slot_map`, `ocfs2_extended_slot`, and `ocfs2_slot_map_extended` define old and extended slot maps.
- `struct ocfs2_cluster_info` stores cluster stack label, flags, and cluster name.
- `struct ocfs2_super_block` is embedded in a dinode and stores revision, state, features, root/system dir blocks, block/cluster geometry, slot count, label, UUID, cluster info, xattr inline size, and indexed-dir hash seeds.
- `struct ocfs2_dinode` is the central inode block, with ownership, size, mode, link count high/low, flags, timestamps, block number, generation, orphan slots, xattr/refcount/dx pointers, checksum, and a union for superblock/local alloc/chain list/extent list/truncate log/inline data/symlink payload.
- Directory structures include packed `ocfs2_dir_entry`, `ocfs2_dir_block_trailer`, `ocfs2_dx_entry`, `ocfs2_dx_entry_list`, `ocfs2_dx_root_block`, and `ocfs2_dx_leaf`.
- Refcount structures include `ocfs2_refcount_rec`, `ocfs2_refcount_list`, and `ocfs2_refcount_block`.
- Xattr structures include `ocfs2_xattr_entry`, `ocfs2_xattr_header`, value/tree roots, and xattr blocks.
- Quota disk structures define global/local quota magic/version arrays, headers, global quota info/records, local quota info/chunks/records, and quota block trailers.

Layout helpers:
- Kernel helpers calculate fast symlink capacity, inline-data capacity with inline xattrs, extent records per dinode/extent block/group descriptor/dx root/refcount block, chain records per inode, dx entries per leaf/root, local alloc bitmap size, group bitmap size, truncate-log capacity, backup superblock locations, xattr records per block, and low 32 bits of refcount record positions.
- Userspace-compatible helper variants are provided outside `__KERNEL__` for several blocksize-based calculations.
- `ocfs2_xattr_set_local()`, `ocfs2_xattr_is_local()`, `ocfs2_xattr_set_type()`, and `ocfs2_xattr_get_type()` manipulate xattr entry type/local bits.
- `ocfs2_set_de_type()` maps inode modes to directory entry file types, and `ocfs2_gd_is_discontig()` identifies discontiguous group descriptors from layout/counter fields.

Dependencies:
- Exposes disk structures to the kernel and userspace OCFS2 tooling; depends on Linux magic numbers, fixed-width little-endian types, and flexible array/count annotations.

Risk and edge cases:
- This header is ABI-sensitive. Field order, sizes, signatures, feature bits, and helper calculations must remain compatible with existing disks and userspace tools.
- Superblock data must fit inside the smallest 512-byte block as embedded in `ocfs2_dinode.id2`; comments explicitly reserve space for that constraint.
- Discontiguous group detection depends on `bg_size` positioning `bg_list` exactly after the filler bitmap and on `l_next_free_rec` being meaningful only in that case.
- Refcount records use 64-bit physical cluster positions while some tree indexing uses low 32 bits; callers must preserve the split/index assumptions.
- The non-kernel `ocfs2_group_bitmap_size()` helper references `sb->s_blocksize` even though its parameter is `blocksize`, which is notable for userspace consumers of this header.
