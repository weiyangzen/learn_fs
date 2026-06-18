# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2.h

Purpose: central in-kernel OCFS2 private header defining metadata-cache state, node maps, DLM lock-resource state, mount/recovery/local-allocation enums, the `ocfs2_super` in-memory superblock, feature/read-only helpers, signature validators, cluster/block/page conversion helpers, and endian-safe bitmap helpers.

Read coverage: complete file read, 993 lines.

Key structures:
- `struct ocfs2_caching_info` tracks metadata buffer uptodate/cache membership with a small inline array that expands to an rb-tree, plus transaction ids protected by `trans_inc_lock`.
- `struct ocfs2_node_map` stores up to 256 cluster node bits.
- `struct ocfs2_lock_res` is the generic OCFS2 cluster lock resource: lock name, type, levels, holder counts, blocked/masked waiter lists, AST/unlock actions, DLM LKSB, waitqueue, debug list, optional stats, and lockdep map.
- `struct ocfs2_orphan_scan` stores the cluster-wide orphan scan lock resource and delayed work state.
- `struct ocfs2_super` is the main per-mount state object, holding VFS superblock pointers, root/system inodes, slot info, feature bits, mount options, generation counters, recovery maps/threads, journal, local allocation state and reservations, quota recovery, ECC/allocation stats, cluster stack connection, super/rename/NFS/trim lock resources, downconvert-thread state, truncate-log state, orphan recovery/wipe tracking, indexed-dir hash state, refcount-tree cache, workqueue, sysfs state, and filecheck state.

Feature and state helpers:
- `ocfs2_should_order_data()` enables ordered data for regular files unless writeback data mode is mounted.
- `ocfs2_sparse_alloc()`, `ocfs2_writes_unwritten_extents()`, `ocfs2_supports_append_dio()`, `ocfs2_supports_inline_data()`, `ocfs2_supports_xattr()`, `ocfs2_meta_ecc()`, `ocfs2_supports_indexed_dirs()`, `ocfs2_supports_discontig_bg()`, and `ocfs2_refcount_tree()` test feature bits copied from the superblock.
- `ocfs2_link_max()`, `ocfs2_read_links_count()`, `ocfs2_set_links_count()`, and `ocfs2_add_links_count()` handle OCFS2's normal and indexed-directory link count formats.
- `ocfs2_set_osb_flag()`, `ocfs2_set_ro_flag()`, `ocfs2_is_hard_readonly()`, `ocfs2_is_soft_readonly()`, `ocfs2_is_readonly()`, and `ocfs2_emergency_state()` coordinate soft/hard read-only mount state under `osb_lock`.
- Cluster-stack helpers identify local mounts, userspace stack, o2cb stack, and o2cb global heartbeat.

Geometry helpers:
- Converts between clusters, blocks, bytes, sectors, megabytes, and page indexes using mounted block size and cluster size.
- `ino_from_blkno()` maps a disk block number into a VFS inode number by truncating to `unsigned long`.
- Provides unaligned little-endian bitmap helpers used where OCFS2 bitmaps may not be naturally word-aligned.

Dependencies:
- Includes stack glue, on-disk format definitions, lock-id definitions, ioctl UAPI definitions, blockcheck stats, reservations, and filecheck state.
- Used throughout OCFS2 by allocation, journal, inode, dcache, DLM glue, quota, refcount, recovery, and superblock code.

Risk and edge cases:
- `struct ocfs2_super` fields have varied locking rules; comments identify critical protection for generation/flags/steal slots, local alloc bits, local alloc state, truncate-log cluster counts, and downconvert lists.
- The lock-resource flags drive asynchronous DLM state transitions; changing flag semantics can break downconvert and upconvert races.
- Feature helpers operate on in-memory feature copies; callers that depend on current disk state must ensure mount/superblock state is initialized and stable.
- `ino_from_blkno()` can truncate block numbers on 32-bit systems unless `OCFS2_MOUNT_INODE64` and VFS/export handling account for it.
