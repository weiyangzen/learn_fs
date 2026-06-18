# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/symlink.c

Implements `ext2fs_symlink`, the libext2fs helper for creating symlink inodes and optionally linking them into a directory. It validates the target length against filesystem block size, allocates an inode if the caller did not supply one, and supports fast symlinks, inline-data symlinks, and regular block-backed symlinks.

Fast symlinks store the target directly in `inode.i_block`. Inline symlinks are attempted when the filesystem has inline-data support; on failure the code falls back to block-backed storage. Regular symlinks allocate one data block, optionally mark the inode extents-based, set the block mapping with `ext2fs_bmap2`, and write the target block through the filesystem I/O channel.

Accounting is updated after inode/block writes. If later linking or setup fails, `drop_refcount` rolls back inode and block allocation stats. The companion `ext2fs_is_fast_symlink` detects symlink inodes with nonzero size smaller than `i_block`.
