# File Research: sources/os/linux/linux-stable/fs/ocfs2/symlink.c

Implements OCFS2 symlink inode operations and fast-symlink page-cache reads.

Key behavior:
- `ocfs2_fast_symlink_read_folio()` reads the inode dinode block with `ocfs2_read_inode_block()`, copies the inline symlink target from `fe->id2.i_symlink` into the requested folio, and completes folio read state.
- The copied length is bounded by `ocfs2_fast_symlink_chars(inode->i_sb)` and includes a terminating NUL.
- `ocfs2_fast_symlink_aops` installs `.read_folio` for fast symlink address spaces.
- `ocfs2_symlink_inode_operations` uses `page_get_link` plus OCFS2 getattr, setattr, listxattr, and fiemap hooks.

Integration points:
- Fast symlinks are detected by `symlink.h` when an inode is a symlink with zero blocks.
- Regular inode/xattr/file attribute paths supply shared operations for symlink metadata.

Risk areas:
- Fast symlink correctness depends on the dinode inline symlink area being valid and shorter than the per-superblock maximum.
- Read errors must end the folio read with failure and release the dinode buffer.
