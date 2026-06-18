# File Research: sources/os/linux/linux-stable/fs/ocfs2/symlink.h

Declares OCFS2 symlink operation tables and the fast-symlink predicate.

Key contents:
- Exposes `ocfs2_symlink_inode_operations`.
- Exposes `ocfs2_fast_symlink_aops`.
- Defines `ocfs2_inode_is_fast_symlink()`, which returns true for symlink inodes with `i_blocks == 0`.

Integration points:
- Inode setup code uses the predicate to choose fast symlink address-space operations.
- VFS symlink handling uses the operation tables implemented in `symlink.c`.

Risk areas:
- The fast-symlink test assumes OCFS2 stores inline symlink targets only for zero-block symlink inodes.
