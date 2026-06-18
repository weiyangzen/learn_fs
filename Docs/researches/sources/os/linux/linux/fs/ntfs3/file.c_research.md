# File Research: sources/os/linux/linux/fs/ntfs3/file.c

## Purpose

Implements regular-file VFS operations for the Linux `ntfs3` driver. This file is the user-facing I/O layer for NTFS files: open, read, write, mmap, fallocate, truncate/extend, fsync, fiemap, ioctl, splice, llseek, and file attributes.

## Main Interfaces

- `ntfs_file_operations`: wires `.read_iter`, `.write_iter`, `.mmap_prepare`, `.open`, `.release`, `.fsync`, `.fallocate`, `.splice_read`, `.splice_write`, `.llseek`, and ioctls.
- `ntfs_file_inode_operations`: wires getattr/setattr, ACL, xattr listing, fiemap, and fileattr retrieval.
- `ntfs_ioctl()` supports `FITRIM`, filesystem label get/set, and `NTFS3_IOC_SHUTDOWN`.
- `ntfs_getattr()` reports NTFS birth time, cluster block size, immutable/append/compressed/encrypted statx attributes.
- `ntfs_setattr()` handles size changes, chmod ACL updates, readonly flag synchronization, and WSL permission persistence.

## Key Behavior

- Direct I/O is attempted only when the inode supports it and position plus iterator alignment match `sbi->bdev_blocksize`; otherwise I/O falls back to buffered paths.
- Reads reject bad inodes, forced-shutdown filesystems, encrypted files, unsupported external compression builds, and deduplicated files.
- Writes reject bad inodes, forced shutdown, encrypted files, deduplicated files, immutable files, and direct I/O to compressed files.
- Compressed native NTFS writes go through `ntfs_compress_write()`, which works frame-by-frame, fills gaps between valid size and write position, reads partial frames when needed, then calls `ni_write_frame()`.
- mmap rejects encrypted and deduplicated files. Writable mmap of compressed files is unsupported. Writable mmap of sparse files preallocates clusters and extends initialized size before mapping.
- `ntfs_filemap_close()` advances `ni->i_valid` for writable mappings whose mapped range was extended.
- `ntfs_extend()` grows file size, marks the volume dirty, extends initialized size through iomap zeroing when needed, updates times, and performs synchronous writeback for sync inodes.
- `ntfs_truncate()` updates page cache size, calls `attr_set_size_ex()`, updates `ni->i_valid`, sets archive bit, and synchronizes for dirsync inodes.
- `ntfs_fallocate()` supports normal preallocation, `KEEP_SIZE`, `PUNCH_HOLE`, `COLLAPSE_RANGE`, and `INSERT_RANGE` with different behavior for sparse/compressed-capable files. It serializes with direct I/O and page-cache invalidation for range surgery.
- `ntfs_file_release()` allocates delayed-allocation clusters on last writer close and removes preallocation when the mount option requests it.
- `ntfs_file_fsync()` flushes file data, inode metadata, parent directory duplicate metadata, clears NTFS dirty state, updates MFT mirror, syncs the block device, and issues a flush.

## Dependencies

- VFS/iomap/page-cache APIs: `generic_file_read_iter`, `iomap_dio_rw`, `iomap_file_buffered_write`, `iomap_zero_range`, `iomap_fiemap`, `filemap_*`.
- NTFS attribute/run helpers: `ntfs_set_size`, `attr_set_size[_ex]`, `attr_data_get_block`, `attr_punch_hole`, `attr_collapse_range`, `attr_insert_range`, `attr_force_nonresident`.
- NTFS inode helpers from `frecord.c`: `ni_allocate_da_blocks`, `ni_read_frame`, `ni_write_frame`, `ni_decompress_file`, `ni_seek_data_or_hole`, `ni_write_parents`.
- Filesystem state helpers: `ntfs_set_state`, `ntfs_trim_fs`, `ntfs_set_label`, `ntfs_update_mftmirr`.

## Error and Safety Notes

- Most public entry points guard `is_bad_ni()` and forced shutdown.
- Privileged ioctls require `CAP_SYS_ADMIN`.
- Unsupported encrypted/deduplicated paths return `-EOPNOTSUPP`, not partial behavior.
- Direct I/O is explicitly incompatible with delayed allocation; delayed blocks are forced before DIO.
- External compressed files are decompressed on write/open with `CONFIG_NTFS3_LZX_XPRESS`; otherwise write access is rejected.
- `ntfs_fallocate()` is the highest-risk path in this file because it combines page-cache invalidation, range mutation, allocation, sparse/compressed distinctions, and size/valid-size updates.
