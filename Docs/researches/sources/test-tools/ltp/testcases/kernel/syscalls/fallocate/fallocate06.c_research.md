# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate06.c

Purpose: Regression test for misaligned allocation and hole punching, with copy-on-write and full-filesystem variants.

Important APIs/types/functions: `fallocate`, `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`, `ioctl(FS_IOC_GETFLAGS/SETFLAGS)`, `FS_NOCOW_FL`, `tst_fill_fs`, `write`, `read`, and buffer validation.

Control flow: `setup()` detects CoW flag support and fills known buffers. Four cases toggle no-CoW and filesystem filling, write initial data, perform misaligned allocation, write into it, punch a misaligned range, and verify only that range was zeroed.

State and persistence behavior: State includes mounted filesystem fullness, inode CoW flag, file block size, written data, and deallocated byte ranges.

Dependencies and integration points: Requires root, a mounted device, minimum device size, all-filesystems coverage, and tags for XFS/Btrfs regressions.

Risks and test signals: Expected `ENOSPC` is tolerated only for the full-FS CoW path. Other errors or incorrect zeroing indicate allocation or deallocation bugs.
