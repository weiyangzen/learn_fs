# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_nodeops.c

Purpose: Implements node-reference list manipulation, obsolete marking, eraseblock accounting transitions, and write-space reservation.

Key entry points:
- `chfs_update_eb_dirty`: moves free space to dirty space for an eraseblock.
- `chfs_add_node_to_list`: inserts node refs into vnode-cache lists sorted by logical eraseblock and offset.
- `chfs_remove_node_from_list`, `chfs_remove_and_obsolete`: unlink node refs, optionally marking them obsolete.
- `chfs_add_fd_to_inode`: inserts/replaces directory entries in an inode’s in-memory dirent list.
- `chfs_add_vnode_ref_to_vc`: keeps only newest vnode metadata node ref.
- `chfs_nref_next`, `chfs_nref_len`: physical node-ref traversal and node length computation.
- `chfs_mark_node_obsolete`: converts used/unchecked node bytes to dirty bytes and moves blocks between queues.
- `chfs_close_eraseblock`: appends a closing node ref, dirties remaining free space, and queues the block.
- `chfs_reserve_space_normal`, `chfs_reserve_space_gc`, `chfs_reserve_space`: reserve append space for normal writes or GC.

Important behavior:
- Obsolete marking updates per-block and mount-wide accounting, sets `CHFS_OBSOLETE_NODE_MASK`, and may trigger block remap if all live bytes are gone.
- Queue migration moves blocks from clean to dirty, dirty to very-dirty, or erase-pending depending on dirty thresholds and live bytes.
- Normal reservation may invoke GC and remap erasable blocks to keep free-block reserves.
- Space reservation closes `chm_nextblock` when it lacks room, flushing/padding the write buffer first.

Dependencies:
- Central dependency for write, unlink, scan, GC, truncate, and fragment cleanup.
- Requires strict lock ordering: usually mountfields, then vnode-cache or sizes depending on operation.

Research notes:
- Contains comments noting “ugly” queue removal and TODOs around reserve-block policy.
- Some paths call `chfs_remap_leb` while still inside accounting/queue logic.
