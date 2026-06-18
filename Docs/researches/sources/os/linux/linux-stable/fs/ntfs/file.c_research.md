# File Research: sources/os/linux/linux-stable/fs/ntfs/file.c

## Scope

This file implements NTFS regular-file VFS operations, inode operations for files/symlinks/special nodes, file IO through iomap, direct IO support, mmap preparation, ioctl handling, and fallocate-style space manipulation.

## APIs And Control Flow

- `ntfs_file_open()` rejects shutdown volumes, enforces 32-bit page-cache size limits, enables `FMODE_NOWAIT` and `FMODE_CAN_ODIRECT`, and delegates to `generic_file_open()`.
- `ntfs_trim_prealloc()` trims unused preallocated hole runs on last close for uncompressed files, updates `allocated_size`, and rewrites mapping pairs.
- `ntfs_file_fsync()` writes file data, the base inode, parent directory index allocation inodes, non-resident named attributes with dirty pages, volume bitmaps, `$MFT`, the block device, and finally issues a flush on success.
- `ntfs_setattr()` handles size changes, generic setattr copying, POSIX ACL chmod updates, readonly attribute synchronization, WSL uid/gid/mode EA updates, and dirty-volume marking.
- `ntfs_getattr()` fills stat data, btime, NTFS compressed/encrypted/immutable/append attributes, block accounting including dealloc clusters, and DIO alignment when supported.
- `ntfs_file_llseek()` supports `SEEK_HOLE` and `SEEK_DATA` through iomap.
- `ntfs_file_read_iter()` supports buffered reads and aligned direct reads; direct reads are rejected for compressed files.
- `ntfs_file_write_iter()` serializes writes, rejects encrypted writes, rejects direct IO for compressed files, runs generic write checks, marks volume dirty, dispatches compressed writes or iomap buffered/direct writes, and rolls back initialized/data size on errors.
- `ntfs_dio_write_iter()` uses iomap direct IO and falls back to buffered writes for `-ENOTBLK`, then writes and invalidates the affected cached range.
- mmap support rejects shutdown and compressed files; writable shared mappings extend initialized size before installing NTFS VM ops.
- `ntfs_ioctl()` implements `FS_IOC_SHUTDOWN`, `FS_IOC_GETFSLABEL`, `FS_IOC_SETFSLABEL`, and `FITRIM`, with privilege checks where needed.
- Fallocate support includes allocate/keep-size, punch-hole, collapse-range, and insert-range. It maps full runlists when needed, waits for known free-cluster counts, marks the volume dirty, serializes DIO/page cache, and calls NTFS non-resident attribute helpers.

## State And Dependencies

This file depends on `iomap` operations from the NTFS iomap layer, attribute truncate/fallocate/punch/collapse/insert helpers, LCN bitmap trimming, WSL EA helpers, POSIX ACL helpers, reparse-tag type lookup, block-device discard/flush APIs, and VFS generic file helpers.

Key state includes `data_size`, `initialized_size`, `allocated_size`, runlists, inode mode/flags, mount masks, dirty volume flags, compression/encryption/sparse bits, and free/dirty cluster counters.

## Risks And Invariants

- Compressed and encrypted files have intentionally limited support: size changes, direct IO, mmap writes, and writes are rejected in several paths.
- Direct IO requires block-size alignment and updates inode size in `end_io`.
- Write error rollback manually restores initialized size and data size; correctness depends on lower-level truncate helpers being able to reverse partial state.
- Fallocate range operations require cluster alignment for collapse/insert and careful cache invalidation before metadata movement.
- Hole punching zeroes partial clusters instead of freeing them, then frees only full-cluster interior ranges.
- `ntfs_file_release()` trims preallocation only for non-compressed files and assumes release means no further writes through that file handle.
