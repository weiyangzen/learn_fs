# sources/test-tools/xfstests/tests/btrfs/120

## Purpose

`sources/test-tools/xfstests/tests/btrfs/120` is btrfs fstests case `120`. It targets log-tree replay and fsync crash recovery, subvolume/snapshot metadata. Source comments describe the scenario as: Test that if we delete a snapshot, delete its parent directory, create another directory with the same name as that parent and then fsync either the new directory or a file inside the new directory, the fsync succeeds, the fsync log is replayable and produces a correct result. Now do the same as before but instead of doing an fsync against the directory, do an fsync against a file inside the directory.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot metadata log` declares tags `auto quick snapshot metadata log`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`, `populate_testdir()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_btrfs subvolume snapshot $SCRATCH_MNT \`; `_btrfs subvolume delete $SCRATCH_MNT/testdir/snap`; `mkdir $SCRATCH_MNT/testdir`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir`; `_flakey_drop_and_remount`; `ls -R $SCRATCH_MNT | _filter_scratch`; `touch $SCRATCH_MNT/testdir/foobar`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir/foobar`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot metadata log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
