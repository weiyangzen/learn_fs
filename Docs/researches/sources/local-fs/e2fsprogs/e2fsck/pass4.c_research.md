# File Research: sources/local-fs/e2fsprogs/e2fsck/pass4.c

This file implements e2fsck pass 4, which validates inode reference counts after earlier passes have discovered allocated inodes, directory references, bad-block inodes, imagic inodes, and extended-attribute inode references.

Main entry point:
- `e2fsck_pass4(e2fsck_t ctx)` iterates every inode from 1 through `s_inodes_count`, skipping reserved/special inodes and inodes excluded by pass-1 maps.
- It compares `ctx->inode_link_info`, the inode’s stored `i_links_count`, and `ctx->inode_count`, the count discovered from directory traversal.
- It frees pass-4-owned structures at completion: `inode_link_info`, `inode_count`, `inode_bb_map`, `inode_imagic_map`, and `ea_inode_refs`.

Important helpers:
- `disconnect_inode()` handles allocated inodes not connected to the directory tree. It can clear zero-length regular files or directories with no blocks and no EA block, or reconnect other unattached inodes to `lost+found`.
- `check_ea_inode()` handles ext4 EA-inode reference accounting. It clears spurious `EXT4_EA_INODE_FL` on normal files when appropriate, treats real EA-inode references as one logical link for pass-4 purposes, and can repair stored EA inode refcounts.

Control flow and repairs:
- Starts readahead of block/inode bitmaps for pass 5 when possible.
- Shows `PR_4_PASS_HEADER` outside preen mode.
- For each live inode, fetches expected link count and observed directory count.
- If EA inode refs exist, consolidates EA-inode status before ordinary link-count checks.
- If observed links are zero, calls `e2fsck_process_bad_inode()` and then `disconnect_inode()`.
- If a directory’s observed link count exceeds `EXT2_LINK_MAX`, enables `dir_nlink` if needed and treats the link count as overflow.
- For mismatched link counts, reports inconsistent cached counts and either fixes `i_links_count` or marks filesystem invalid if the user declines.

Integration points:
- Uses `problem.h` codes `PR_4_*` and central `fix_problem()` prompting.
- Uses ext2fs inode bitmaps and icount APIs.
- Updates quota accounting when deleting zero-length disconnected inodes.
- Coordinates with `lost+found` reconnection and pass-5 bitmap loading.

Risk notes:
- The loop is protected against inode-number wraparound.
- `last_ino` avoids repeated inode reads but is reset after reconnection.
- EA-inode logic distinguishes old Lustre-style EA inodes by `i_ctime == i_atime`.
- Repair decisions depend heavily on user/preen policy from `problem.c`.
