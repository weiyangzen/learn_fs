# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_inode.c

Read status: complete, 314 lines.

Purpose: reads VxFS disk inodes into Linux inodes and assigns VFS operations.

Key flow:
- `vxfs_transmod()` translates VxFS mode/type bits to Linux `S_IF*` mode bits.
- `dip2vip_cpy()` endian-converts stable inode fields, copies organization-specific data raw, and populates VFS uid/gid/nlink/size/timestamps/blocks/generation.
- `vxfs_blkiget()` reads an inode directly from a specified disk extent via buffer cache for mount-time structural metadata.
- `__vxfs_iget()` reads an inode from an inode-list file via page cache.
- `vxfs_stiget()` creates structural inodes from the structural inode list.
- `vxfs_iget()` uses `iget_locked()` for normal inodes, reads from `vsi_ilist`, assigns regular file, directory, symlink, or special inode operations, and handles immediate symlink data.
- `vxfs_evict_inode()` truncates pages and clears the inode.

Important dependencies: inode-list setup from `vxfs_fshead.c`, page helpers in `vxfs_subr.c`, directory ops, immediate and normal address-space ops.

Risk notes:
- Structural inode reads use `new_inode()` with generated inode numbers, distinct from normal cached inode lookup.
- Organization-specific fields are not endian-swapped until interpreted by later mapping code.
