# File Research: sources/os/linux/linux/fs/ocfs2/symlink.h

## Purpose

`symlink.h` declares OCFS2 symlink operation tables and provides the inline predicate for detecting fast symlinks.

## API Surface

- `ocfs2_symlink_inode_operations`
- `ocfs2_fast_symlink_aops`
- `ocfs2_inode_is_fast_symlink(struct inode *inode)`

## Fast Symlink Predicate

`ocfs2_inode_is_fast_symlink()` returns true when:

- The inode mode is a symbolic link.
- `inode->i_blocks == 0`.

This matches the OCFS2 convention that fast symlink contents are stored inline in the inode rather than in allocated data blocks.
