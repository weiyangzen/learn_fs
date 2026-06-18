# File Research: sources/local-fs/mtd-utils/tests/fs-tests/integrity/integck.c

## Purpose
Full filesystem integrity stress test for a mounted test filesystem. It randomly creates, mutates, syncs, renames, unlinks, and remounts files/directories/symlinks/hardlinks, while maintaining an in-memory model of expected state and data contents.

## Key Elements
Defines models for `write_info`, `file_info`, `dir_info`, `dir_entry_info`, `symlink_info`, and open file descriptors. Writes deterministic random byte streams and records range metadata so later checks can validate file length, holes, data, link counts, symlink targets, and directory entries. `create_test_data()` fills then partially drains the FS; `update_test_data()` repeats growth/shrink/mutation cycles; `integck()` creates the test tree, remounts, verifies, repeats, and cleans up.

## Dependencies
Uses POSIX filesystem APIs, `statvfs/statfs`, `mmap`, mount table parsing, `mount/umount`, `backtrace`, project `common.h`, and `libubi.h` for optional UBI reattach in power-cut mode.

## Behavior/Risks
Highly destructive inside the specified mount point and may unmount/remount it. Power-cut mode expects failures as `EROFS` or sometimes `EIO`, can reattach `/dev/ubi_ctrl` MTD devices, and runs indefinitely. Uses `d_type` from `readdir()`, root privileges for remounts, and many `CHECK()` exits on invariant violation.
