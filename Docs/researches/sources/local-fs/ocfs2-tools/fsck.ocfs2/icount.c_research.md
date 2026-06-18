# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/icount.c

Read coverage: complete file read, 242 lines.

Purpose: compact inode reference/link count table used by fsck.

Behavior:
- Represents count `1` in a block bitmap and counts greater than `1` in an rb-tree keyed by inode block number.
- `o2fsck_icount_set()` keeps bitmap and tree synchronized.
- `o2fsck_icount_get()` reads either the single-count bitmap or multi-count tree.
- `o2fsck_icount_delta()` adjusts counts and logs internal failure on negative transitions.
- `o2fsck_icount_next_blkno()` finds the next inode with a recorded count across both structures.
- `o2fsck_icount_new()` allocates state; `o2fsck_icount_free()` releases bitmap and tree nodes.

Dependencies: OCFS2 block bitmap APIs and kernel-style rbtrees.

Risk notes:
- Insert helper assumes duplicates are not inserted.
- Count storage is `uint16_t`, matching OCFS2 link-count scale but requiring caller discipline for overflows.
