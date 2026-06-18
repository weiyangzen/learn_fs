# File Research: sources/os/linux/linux/fs/ntfs/file.c

## Purpose
Provides NTFS regular-file VFS operations: open/release, fsync, setattr/getattr, read/write iterators, mmap preparation, fiemap, symlink target lookup, filesystem ioctls, and fallocate range operations.

## Key Elements
`ntfs_file_open()` rejects shutdown volumes, enforces 32-bit page-cache limits, and enables nowait and direct-I/O capability. `ntfs_file_release()` trims unused preallocated hole runlist tail space for non-compressed files. `ntfs_file_fsync()` writes dirty page ranges, MFT records, parent directory index allocations, dirty non-resident named attributes, volume bitmaps, `$MFT`, the block device, and issues a flush on success.

Size and metadata changes go through `ntfs_setattr()` and `ntfs_setattr_size()`, which reject compressed/encrypted size changes, update NTFS readonly flags, apply masks, and persist uid/gid/mode to WSL EAs. `ntfs_getattr()` reports NTFS birth time, compressed/encrypted/immutable/append attributes, adjusted block counts, and DIO alignment for normal regular files.

Read/write paths use iomap: buffered reads delegate to `generic_file_read_iter()`, aligned direct reads use `iomap_dio_rw()`, writes support compressed-file writes through `ntfs_compress_write()`, direct writes with buffered fallback, and buffered iomap writes. Error paths roll back initialized size and data size when possible. mmap write faults are handled by iomap page-mkwrite and shared writable mappings pre-extend initialized size.

The ioctl layer supports forced shutdown, get/set filesystem label, compat ioctl forwarding, and FITRIM. Fallocate supports allocate/keep-size, punch hole, collapse range, and insert range by combining page-cache invalidation, cluster alignment checks, sparse checks, runlist transformations, and inode size updates.

## Dependencies And Integration
Depends on Linux writeback, blkdev, iomap, uio, compat, fallocate, POSIX ACL, file locks, plus NTFS allocation, reparse, EA, iomap, and bitmap helpers. Exports `ntfs_file_ops`, regular-file inode ops, symlink inode ops, special inode ops, and empty ops used for inaccessible system files such as `$MFT`.

## Behavior/Risks
Compressed and encrypted files have intentionally limited support: no encrypted writes, no compressed DIO, no compressed mmap, and no compressed/encrypted size or fallocate transformations. Range operations require cluster alignment except punch-hole edge zeroing. Many operations mark the volume dirty before metadata-changing writes.
