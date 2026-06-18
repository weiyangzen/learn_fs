# sources/test-tools/xfstests/tests/btrfs/209

## Purpose

`sources/test-tools/xfstests/tests/btrfs/209` is btrfs fstests case `209`. It targets log-tree replay and fsync crash recovery, mmap/msync persistence. Source comments describe the scenario as: Test a scenario were we fsync a range of a file and have a power failure. We want to check that after a power failure and mounting the filesystem, we do not end up with a missing file extent representing a hole. This applies only when not using the NO_HOLES feature. Create a 256K file with a single extent and fsync it to clear the full sync bit from the inode - we want the msync below to trigger a fast fsync. Force a transaction commit and wipe out the log tree. Dirty 768K of data, increasing the file size to 1Mb, and flush only the range from 256K to 512K without updating the log tree (sync_file_range() does not trigger fsync, it only starts writeback and waits for it to finish).

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick log mmap` declares tags `auto quick log mmap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/attr`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_xfs_io_command "sync_range"`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_require_btrfs_fs_feature "no_holes"`; `_init_flakey`; `_scratch_mount`; `-c "pwrite -S 0xab 0 256K" \`; `-c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0xcd 256K 768K" \`; `-c "msync -s 768K 256K"       \`; `echo "File digest before power failure: $(_md5_checksum $SCRATCH_MNT/foo)"`; `_flakey_drop_and_remount`; `echo "File digest after power failure: $(_md5_checksum $SCRATCH_MNT/foo)"`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick log mmap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
