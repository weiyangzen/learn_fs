# File Research: sources/os/linux/linux-stable/fs/omfs/omfs.h

## Scope

This internal header defines the OMFS in-memory superblock state, cluster-to-block conversion, accessor macro, and cross-file function/operation declarations.

## Data Model

- `struct omfs_sb_info` stores total blocks, bitmap inode, root inode, data/system block sizes, mirror count, cluster size, block-shift conversion factor, in-memory bitmap array, bitmap lock, uid/gid, and directory/file masks.
- `clus_to_blk()` converts OMFS cluster/block numbers to Linux sector/block numbers by left-shifting with `s_block_shift`.
- `OMFS_SB()` retrieves the OMFS private superblock from `sb->s_fs_info`.

## Declarations

- Bitmap operations: count free, allocate exact block, allocate range, clear range.
- Directory operations and helpers: directory file/inode ops, empty inode initialization, bad-chain detection.
- File operations and helpers: regular file ops, inode ops, address-space ops, empty extent table creation, shrink inode.
- Inode helpers: OMFS block read, iget, new inode, sync inode.

## Notes

- Declarations `omfs_reserve_block()` and `omfs_find_empty_block()` appear in this header but are not implemented in the listed OMFS files, suggesting stale prototypes.
