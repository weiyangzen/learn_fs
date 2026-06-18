# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass0.c

Purpose: implements fsck pass 0 for OCFS2, validating and repairing the structural linkage of cluster, inode, and extent block chain allocators before later passes rely on allocator iteration.

Read coverage: complete file read, 1,573 lines.

Key responsibilities:
- Verifies global bitmap chain allocator descriptors, including the special rule that cluster bitmap group descriptors live at predictable block offsets.
- Verifies global and per-slot inode allocation chains, then loads their cached chain allocator state into `ost_global_inode_alloc` and `ost_inode_allocs` for pass 1.
- Verifies per-slot extent allocation chains.
- Repairs group descriptor metadata: generation, parent dinode, recorded block number, chain number, free-bit counts, discontiguous group extent-list fields, and chain/inode aggregate counts.
- Detects bad chain links, out-of-range group references, invalid descriptor magic/generation, duplicate descriptors, and loops; can truncate a chain or break loops.
- Reinitializes and relinks expected global bitmap descriptors that are missing from their chains.
- Handles global bitmap size disagreements with the superblock after failed resize-like operations and reinitializes fsck state if the user chooses to trust the repaired global bitmap.

Important entry points:
- `o2fsck_pass0()` runs pass 0a, 0b, and 0c.
- `verify_bitmap_descs()` checks predictable global bitmap descriptors and reconciles allowed/forbidden descriptor bitmaps.
- `verify_chain_alloc()` validates generic chain allocator inodes.
- `check_chain()` walks one chain record and repairs or truncates damaged links.
- `repair_group_desc()`, `check_discontig_bg()`, and `unlink_group_desc()` perform descriptor-level repair.
- `maybe_fix_clusters_per_group()` fixes an old mkfs edge case for single-group global bitmaps.
- `break_loop()` severs group descriptor cycles.

Dependencies:
- Uses libocfs2 chain allocator, group descriptor, bitmap, system inode, cached inode, and block/cluster conversion APIs.
- Uses fsck state bitmaps to mark allocator metadata clusters as in use.
- Uses `prompt()` problem codes for all user-authorized repairs and resource tracking helpers from `util.c`.

Risk and edge cases:
- Later passes assume pass 0 left allocator chains iterable; unrepaired damage can abort the fsck run.
- Global bitmap repair can change `fs_clusters` and force `o2fsck_state_reinit()`, requiring a retry of bitmap descriptor scanning.
- `unlink_group_desc()` updates allocator counts after unlinking a descriptor and comments note rollback would be difficult if the inode write fails.
- Discontiguous block group repair must decide between correcting a single bad extent length and dropping the entire group when the extent list is inconsistent.
- If `cl_next_free_rec` is not trusted, empty chain removal is refused because shifting records would be unsafe.
