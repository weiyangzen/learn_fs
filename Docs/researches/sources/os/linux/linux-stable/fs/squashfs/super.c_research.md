# File Research: sources/os/linux/linux-stable/fs/squashfs/super.c

## Summary
Implements Squashfs mount parsing, superblock validation, in-memory setup, unmount cleanup, statfs, inode-cache allocation, and filesystem registration.

## Key APIs
- Filesystem type `squashfs_fs_type`.
- Super operations `squashfs_super_ops`.
- Mount context operations for get-tree, parse-param, reconfigure, and free.

## Important Behavior
Mount options support `errors=continue|panic` and, when configured, `threads=` by name or numeric count. Default decompressor thread ops are chosen from Kconfig.

`squashfs_fill_super()` sets the device block size, reads the superblock with a temporary `bytes_used`, checks magic, version, compression support, filesystem size against the block device, block size/log consistency, page-size compatibility, and root inode offset.

It allocates metadata and data caches, optional compressed-page cache mapping when device blocks are page-sized, decompressor stream state, xattr id tables, id tables, inode lookup table/export ops, fragment cache/index, then validates table ordering before reading and installing the root inode.

The filesystem is always mounted read-only. `squashfs_statfs()` reports compressed-image block usage, inode count, no free blocks/inodes, max name length, and an fsid derived from the block device.

## Cleanup and Lifetime
Partial mount failure and `squashfs_put_super()` delete caches, drop the optional cache inode, destroy decompressor streams, free table arrays and meta-index state, and free `s_fs_info`. The module owns a slab cache for `squashfs_inode_info`.

## Risks
Mount ordering matters because later table boundaries are derived from earlier optional tables. The cleanup path must tolerate partially initialized state. The filesystem type advertises `FS_ALLOW_IDMAP`, while inode uid/gid mapping is still performed by VFS stat helpers.
