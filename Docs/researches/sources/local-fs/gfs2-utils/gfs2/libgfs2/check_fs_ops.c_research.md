# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_fs_ops.c

This file contains Check unit tests for selected `fs_ops.c` behaviors and allocation APIs.

It builds mock filesystem fixtures using a temporary unlinked file as a block device. `mockup_fs()` creates an `lgfs2_sbd`, sizes the mock device, sets block size, and computes constants. `mockup_rgs()` plans and appends resource groups, allocates bit buffers, and attaches them to the mock superblock.

Test cases:
- `test_lookupi_bad_name_size()` verifies zero-length and too-long names fail with `ENAMETOOLONG`.
- `test_lookupi_dot()` verifies `"."` lookup returns the input directory inode.
- `test_lookupi_dotdot()` constructs a stuffed directory block containing `.` and `..` and verifies lookup returns a separate parent inode.
- `test_dinode_alloc()` verifies failed oversized dinode allocation does not change counters, then checks successful allocation updates counters and bitmap state.
- `test_meta_alloc()` verifies metadata allocation updates block counters and bitmap state.

`suite_fs_ops()` organizes tests into Check test cases with appropriate fixtures.

Risks and notes:
- Tests use fixed mock sizes and block size.
- The dotdot test hand-builds on-disk dirents, so it validates exact dirent layout assumptions.
