# sources/test-tools/xfstests/tests/btrfs/206

## Purpose

`sources/test-tools/xfstests/tests/btrfs/206` is btrfs fstests case `206`. It targets log-tree replay and fsync crash recovery. Source comments describe the scenario as: Validate that without no-holes we do not get a i_size that is after a gap in the file extents on disk when punching a hole past i_size.  This is fixed by the following patches btrfs: use the file extent tree infrastructure btrfs: replace all uses of btrfs_ordered_update_i_size block-group-tree requires no-holes There's not a straightforward way to commit the transaction without also flushing dirty pages, so shorten the commit interval to 1 so we're sure to get a commit with our broken file This creates a gap extent because fpunch doesn't insert hole extents past

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick log replay recoveryloop punch prealloc` declares tags `auto quick log replay recoveryloop punch prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmlogwrites`; requirements: `_require_test`, `_require_scratch`, `_require_log_writes`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fpunch"`, `_require_btrfs_no_block_group_tree`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_require_btrfs_no_block_group_tree`; `_log_writes_mkfs "-O ^no-holes" >> $seqres.full 2>&1`; `_log_writes_mount -o commit=1`; `$XFS_IO_PROG -f -c "falloc -k 4k 8k" $SCRATCH_MNT/file`; `$XFS_IO_PROG -f -c "fpunch 4k 4k" $SCRATCH_MNT/file`; `$XFS_IO_PROG -f -c "pwrite 0 4k" $SCRATCH_MNT/file | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite 0 8k" $SCRATCH_MNT/file | _filter_xfs_io`; `$XFS_IO_PROG -f -c "truncate 12k" $SCRATCH_MNT/file`; `_log_writes_unmount`; `_check_scratch_fs`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick log replay recoveryloop punch prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
