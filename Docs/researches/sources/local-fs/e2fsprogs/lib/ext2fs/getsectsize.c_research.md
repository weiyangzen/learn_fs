# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/getsectsize.c

## Role

Queries logical sector size, direct-I/O alignment, and physical sector size for a device/file.

## Main Flow

- `ext2fs_get_device_sectsize()` opens the path and tries `BLKSSZGET` or `DIOCGSECTORSIZE`; returns zero sector size if unknown.
- `ext2fs_get_dio_alignment()` tries ioctl sector size, then page size, then defaults to 4096.
- `ext2fs_get_device_phys_sectsize()` tries `BLKPBSZGET`, falls back to FreeBSD sector size, and returns zero if unknown.
- Windows logical/physical sector helpers return or reuse a 512-byte guess.

## Dependencies

Uses platform ioctl constants and `ext2fs_open_file()`.

## Risks / Notes

- Unknown sector size is represented as success with `*sectsize = 0`, not an error.
- Physical sector size may be approximated by logical sector size on platforms without a separate concept.
