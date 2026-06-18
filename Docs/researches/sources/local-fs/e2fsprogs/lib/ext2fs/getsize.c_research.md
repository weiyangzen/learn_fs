# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/getsize.c

## Role

Determines a device or regular file size in filesystem blocks.

## Main Flow

- Windows path tries partition info, drive geometry, then file size.
- Unix path tries Darwin, Linux `BLKGETSIZE64`, older `BLKGETSIZE`, floppy geometry, BSD disklabel/media-size ioctls, regular-file `stat`, and finally binary search over readable offsets.
- `ext2fs_get_device_size()` wraps the 64-bit version and returns `EFBIG` if the result exceeds 32-bit blocks.

## Dependencies

Uses platform ioctls, `ext2fs_open_file`, `ext2fs_llseek`, `ext2fs_fstat`, and libc read/stat calls.

## Risks / Notes

- Linux 2.4 `BLKGETSIZE64` is explicitly avoided due historical unreliability.
- Binary search fallback is slow and depends on readable offsets.
- The debug `main` contains a typo in the printed variable name (`locks`), but it is compiled only under `DEBUG`.
