# sources/test-tools/xfstests/tests/btrfs/118

## Purpose

`sources/test-tools/xfstests/tests/btrfs/118` is btrfs fstests case `118`. It targets log-tree replay and fsync crash recovery, subvolume/snapshot metadata. Source comments describe the scenario as: Test that if we fsync a directory that had a snapshot entry in it that was deleted and crash, the next time we mount the filesystem, the log replay procedure will not fail and the snapshot is not present anymore. Create a snapshot at the root of our filesystem (mount point path), delete it, fsync the mount point path, crash and mount to replay the log. This should succeed and after the filesystem is mounted the snapshot should not be visible anymore. Similar scenario as above, but this time the snapshot is created inside a directory and not directly under the root (mount point path).

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot metadata log` declares tags `auto quick snapshot metadata log`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume delete $SCRATCH_MNT/snap1`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT`; `_flakey_drop_and_remount`; `mkdir $SCRATCH_MNT/testdir`; `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/testdir/snap2`; `_btrfs subvolume delete $SCRATCH_MNT/testdir/snap2`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot metadata log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
