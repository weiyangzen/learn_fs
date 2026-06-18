# File Research: sources/local-fs/e2fsprogs/misc/check_fuzzer.c

## Purpose
Small regression helper for quickly exercising libext2fs paths on a filesystem image to find UBSAN/fuzzer-triggered problems.

## Main Behavior
- Opens the supplied filesystem/device with `ext2fs_open()` and `unix_io_manager`.
- Reads inode and block bitmaps.
- Calls `ext2fs_check_directory()` on the root inode.
- Reports errors with `com_err` and exits nonzero on failure.

## Integration
Built by `misc/Makefile.in` as `check_fuzzer`.

## Risks / Notes
It is intentionally narrow and diagnostic; it does not perform repair.
