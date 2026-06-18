# File Research: sources/os/linux/linux-stable/fs/ocfs2/resize.c

Purpose: implements OCFS2 online volume growth by extending the last cluster group or adding a new group descriptor to the global bitmap.

Read coverage: complete file read, 598 lines.

Key responsibilities:
- Marks backup superblock locations in group bitmaps when growth exposes new backup-super clusters.
- Updates the last group descriptor, global bitmap inode chain accounting, inode size, and in-memory cluster count.
- Writes primary and backup superblocks after bitmap growth.
- Validates externally created new group descriptors before linking them into the global bitmap chain.

Major logic:
- `ocfs2_calc_new_backup_super()` identifies backup superblock clusters that newly fall into the last group and sets or clears corresponding bitmap bits.
- `ocfs2_update_last_group_and_inode()` journals group descriptor and bitmap inode changes for `ocfs2_group_extend()`, with rollback of group fields if inode journaling fails.
- `ocfs2_update_super_and_backups()` updates the primary superblock’s cluster count and then updates backup superblocks best-effort.
- `ocfs2_group_extend()` locks the global bitmap system inode, validates that the current last group can be extended, updates last group and bitmap inode state, and updates superblocks.
- `ocfs2_verify_group_and_input()` validates that a new group is beyond current volume size, chain selection is valid, the previous last group is full, counts do not overflow, and the supplied group block number is correct.
- `ocfs2_group_add()` reads and validates a new group descriptor, links it at the head of the selected bitmap chain, updates chain totals/free counts, bitmap totals/used counts, inode cluster/size state, and superblocks.

Concurrency and dependencies:
- Both public paths reject emergency read-only state.
- Operations lock the global bitmap inode with VFS inode mutex and OCFS2 inode cluster lock.
- Uses OCFS2 journaling, group descriptor validation, system inode lookup, bitmap chain accounting, suballocator helpers, and synchronous superblock write helpers.

Risks and edge cases:
- Online resize only supports modern full-sized group bitmaps; older/small layouts are rejected and must use offline resize.
- `ocfs2_group_extend()` can only extend the current last group up to `cl_cpg`; adding beyond that requires `ocfs2_group_add()`.
- Backup superblock update failures are reported as nonfatal with a recommendation to run fsck.
- New group descriptors are expected to already exist on disk and match caller-supplied input exactly.
