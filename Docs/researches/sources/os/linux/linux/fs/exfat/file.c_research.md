# File Research: sources/os/linux/linux/fs/exfat/file.c

## Purpose
Implements regular-file VFS operations, file resizing/truncation policy, fallocate, attribute/stat handling, ioctls, fsync, valid-data-length maintenance, mmap write handling, and read/write/splice dispatch.

## Main Interfaces
- File ops: `exfat_file_operations`
- Inode ops: `exfat_file_inode_operations`
- Exported helpers: `__exfat_truncate`, `exfat_truncate`, `exfat_setattr`, `exfat_getattr`, `exfat_fileattr_get`, `exfat_file_fsync`, `exfat_ioctl`, `exfat_compat_ioctl`

## Key Data Flow
`exfat_cont_expand()` grows allocation without extending valid data length, supporting `FALLOC_FL_ALLOCATE_RANGE` and expanding truncate. `__exfat_truncate()` updates directory metadata before freeing clusters to reduce crash windows where freed clusters remain referenced.

`exfat_setattr()` enforces exFAT’s limited ownership/mode model, handles growth via allocation, zeroes partial truncate blocks, updates inode state, and calls `exfat_truncate()`. Read/write paths reject forced shutdown, maintain valid size, zero gaps before writes beyond VDL, validate direct-I/O alignment, and use generic buffered/direct I/O helpers.

Ioctls expose FAT-style attribute get/set, shutdown, FITRIM, and filesystem label get/set.

## Dependencies
Depends on inode/block mapping in `inode.c`, cluster allocation/free in `fatent.c`, volume-label functions in `dir.c`, NLS conversion, security hooks, block-device flush/discard, and VFS generic file helpers.

## Notable Invariants And Risks
- `valid_size` and `i_size` intentionally differ; unwritten allocated ranges must read as zero.
- Attribute updates must respect root-directory restrictions and capability checks for system attributes.
- `fsync` flushes file state, the block device, and cache.
