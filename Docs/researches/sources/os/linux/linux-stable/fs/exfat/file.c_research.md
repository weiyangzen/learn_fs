# File Research: sources/os/linux/linux-stable/fs/exfat/file.c

This file implements regular-file VFS operations, attribute ioctls, fitrim/label/shutdown ioctls, fallocate, truncate/expand behavior, valid-size extension, mmap write handling, and fsync.

Key elements:
- `exfat_cont_expand()` grows a file by allocating clusters, linking them to the existing chain, updating `i_size`, `i_blocks`, times, and dirty state without increasing `valid_size`.
- `exfat_fallocate()` supports only `FALLOC_FL_ALLOCATE_RANGE`, implemented as expansion without zeroing newly allocated clusters because exFAT tracks valid data length.
- `__exfat_truncate()` adjusts FAT/bitmap state after shrink or zero-length truncation, writes directory metadata before freeing clusters, invalidates cluster cache, resets hints, and frees the removed chain.
- `exfat_setattr()` handles size expansion/shrink, ownership/mode restrictions derived from mount options, timestamp permission relaxation via `allow_utime`, and atime truncation.
- Attribute ioctls map FAT/exFAT attributes to Unix mode and restrict system attribute changes to `CAP_LINUX_IMMUTABLE`.
- `FITRIM`, forced shutdown, and filesystem label ioctls dispatch to allocation, shutdown, and volume-label helpers.
- `exfat_file_write_iter()` ensures holes between `valid_size` and write position are zeroed before writes.
- `exfat_extend_valid_size()` writes zeroed buffers up to a new valid-size boundary.
- `exfat_page_mkwrite()` extends valid size for mmap writes before allowing page dirtying.
- `exfat_file_fsync()` flushes file data, block device state, and cache flush.

Important dependencies:
- Uses `fatent.c` allocation/free/chain logic and `inode.c` writeback/block mapping.
- Uses `dir.c` volume label helpers and `nls.c` conversion for label ioctl paths.
- Uses `misc.c` timestamp truncation and buffer update utilities.

Failure/edge behavior:
- Most public operations reject work after forced shutdown.
- Direct I/O write alignment must satisfy inode block size or device logical block size.
- Truncation writes directory entry metadata before freeing clusters to reduce power-failure dangling-reference risk.
