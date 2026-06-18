# sources/test-tools/xfstests/tests/btrfs/211

## Purpose

`sources/test-tools/xfstests/tests/btrfs/211` is btrfs fstests case `211`. It targets log-tree replay and fsync crash recovery. Source comments describe the scenario as: Test that if we fsync a file with prealloc extents that start before and after the file's size, we don't end up with missing parts of the extents and implicit file holes after a power failure. Test both without and with the NO_HOLES feature. fiemap needed by _count_extents() Create our test file with 2 consecutive prealloc extents, each with a size of 128Kb, and covering the range from 0 to 256Kb, with a file size of 0. Then fsync the file to record both extents in a log tree. Now do a redudant extent allocation for the range from 0 to 64Kb. This will merely increase the file size from 0 to 64Kb. Instead we could also do a

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick log prealloc fiemap` declares tags `auto quick log prealloc fiemap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fiemap"`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`, `run_test()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_require_btrfs_fs_feature "no_holes"`; `_require_dm_target flakey`; `$XFS_IO_PROG -f -c "falloc -k 0 128K" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "falloc -k 128K 128K" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "falloc 0 64K" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "truncate 256K" -c "fsync" $SCRATCH_MNT/foo`; `_scratch_mount`; `$XFS_IO_PROG -c "pwrite -S 0xab 0 128K" $SCRATCH_MNT/foo | _filter_xfs_io`; `_scratch_mkfs -O ^no-holes >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mkfs -O no-holes >>$seqres.full 2>&1`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick log prealloc fiemap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
