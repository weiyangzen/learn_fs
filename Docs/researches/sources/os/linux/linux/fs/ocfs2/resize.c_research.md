# File Research: sources/os/linux/linux/fs/ocfs2/resize.c

`resize.c` implements online OCFS2 volume resize support for extending the global bitmap, either by growing the last existing group or by adding a new group descriptor.

Main responsibilities:
- Handles backup superblock accounting:
  - `ocfs2_calc_new_backup_super()` finds backup superblock locations newly covered by the last group extension and sets or clears their bits in the group bitmap.
  - `update_backups()` writes updated superblock contents to each existing backup location.
  - `ocfs2_update_super_and_backups()` updates the primary superblock cluster count and best-effort backup superblocks; backup update failure is reported as non-fatal with an fsck recommendation.
- Extends the last global bitmap group:
  - `ocfs2_group_extend()` rejects emergency-readonly state, negative sizes, old/small bitmap formats requiring offline resize, and extensions beyond the current group’s capacity.
  - It locks the global bitmap inode, validates the dinode, reads the last group descriptor, starts a journal transaction, and calls `ocfs2_update_last_group_and_inode()`.
  - `ocfs2_update_last_group_and_inode()` increases group bit counts, free counts, contiguous-free tracking, chain totals, bitmap inode clusters/size, and accounts backup superblock bits as used.
  - It rolls back group descriptor fields if inode update journaling fails.
- Adds a new global bitmap group:
  - `ocfs2_group_add()` reads the new group descriptor from disk, validates it, links it into the requested chain, updates chain totals/free counts, bitmap totals/used counts, bitmap inode clusters/size, and superblocks.
  - `ocfs2_verify_group_and_input()` checks that the group is outside the current volume, in a valid chain, does not overflow cluster totals, is not larger than clusters-per-group, does not follow a partial last group, and maps to the expected cluster group block.
  - `ocfs2_check_new_group()` validates the group descriptor itself and compares chain, bit count, and free count against userspace input.

Key invariants:
- Resize operations are refused in OCFS2 emergency state.
- The global bitmap inode is locked with VFS inode mutex and OCFS2 inode cluster lock before modification.
- Old bitmap formats with smaller cluster-per-group layouts require offline resize.
- Adding a group is allowed only when the previous last group is full; otherwise callers must use group extend first.
- Superblock and backup updates happen after bitmap metadata updates; backup write failure is not treated as fatal to the resize transaction.
