# File Research: sources/os/linux/linux/fs/ocfs2/symlink.c

## Purpose

`symlink.c` implements OCFS2 symlink inode operations, including a fast-symlink read path for symlink targets stored inline in the inode dinode.

## Fast Symlink Read

`ocfs2_fast_symlink_read_folio()`:

- Gets the target inode from `folio->mapping->host`.
- Reads the inode block with `ocfs2_read_inode_block()`.
- Treats `fe->id2.i_symlink` as the inline symlink target.
- Uses `strnlen()` bounded by `ocfs2_fast_symlink_chars(inode->i_sb)`.
- Copies the string plus NUL terminator into the folio with `memcpy_to_folio()`.
- Ends folio read with success based on the inode-block read status and releases the buffer head.

The address-space operation table `ocfs2_fast_symlink_aops` installs this as `.read_folio`.

## Inode Operations

`ocfs2_symlink_inode_operations` provides:

- `.get_link = page_get_link`
- `.getattr = ocfs2_getattr`
- `.setattr = ocfs2_setattr`
- `.listxattr = ocfs2_listxattr`
- `.fiemap = ocfs2_fiemap`

## Dependencies

This file uses inode read helpers, file attribute handling, xattr listing, and fiemap from other OCFS2 subsystems. The fast-symlink predicate is declared in `symlink.h`.

## Correctness Notes

- Fast symlink length is bounded by filesystem-specific inline symlink capacity before copying.
- The read path copies the NUL terminator so `page_get_link` can return a normal string.
- Errors from reading the inode block propagate through `folio_end_read(folio, false)`.
