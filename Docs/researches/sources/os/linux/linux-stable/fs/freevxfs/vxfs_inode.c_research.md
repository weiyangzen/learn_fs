# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_inode.c

This file decodes VxFS disk inodes into Linux VFS inodes and selects the correct VFS operations for regular files, directories, symlinks, and special files.

Major responsibilities:
- Translate VxFS mode/type bits into Linux `umode_t`.
- Copy and endian-convert stable disk inode fields into `struct vxfs_inode_info`.
- Read inodes directly from a known extent during early mount setup.
- Read inodes through structural or primary inode-list files after metadata setup.
- Set VFS inode ownership, size, times, blocks, generation, mapping operations, file operations, inode operations, and special device numbers.
- Handle immediate-data files and symlinks.
- Evict VxFS inodes by truncating pagecache and clearing the VFS inode.

Important design points:
- `vxfs_blkiget()` uses buffer-cache reads and is intended only during `read_super` style setup before normal inode lists are available.
- `__vxfs_iget()` uses the pagecache against the inode-list inode, allowing normal cached reads.
- `vxfs_stiget()` reads from the structural inode list; `vxfs_iget()` reads from the primary inode list and uses `iget_locked()`.
- Organization-specific data is copied without endian conversion because the active union layout depends on `vii_orgtype`; mapping code converts fields when interpreting them.
- Immediate symlinks terminate the inline link buffer and point `i_link` into the inode-private immediate data.

Key invariants:
- New VFS inodes must remain locked until fully initialized or failed via `iget_failed()`.
- Regular files use `generic_ro_fops`; directories use FreeVxFS lookup/readdir operations.
- Non-immediate symlinks use page-backed symlink operations and disallow highmem.
- Special inodes use `old_decode_dev(vii_rdev)`.
- Eviction does not write data because the filesystem is read-only.

External interfaces:
- Provides `vxfs_blkiget`, `vxfs_stiget`, `vxfs_iget`, `vxfs_evict_inode`, and optional diagnostic inode dumping.
