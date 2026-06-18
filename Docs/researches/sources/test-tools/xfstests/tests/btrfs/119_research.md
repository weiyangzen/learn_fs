# sources/test-tools/xfstests/tests/btrfs/119

## Purpose

`sources/test-tools/xfstests/tests/btrfs/119` is btrfs fstests case `119`. It targets log-tree replay and fsync crash recovery, subvolume/snapshot metadata, quota-group accounting and limits. Source comments describe the scenario as: Test log tree replay when qgroups are enabled and orphan roots (deleted snapshots) exist. Create 2 directories with one file in one of them. We use these just to trigger a transaction commit later, moving the file from directory a to directory b and doing an fsync against directory a. Create our test file with 2 4K extents. Create a snapshot and delete it. This doesn't really delete the snapshot immediately, just makes it inaccessible and invisible to user space, the snapshot is deleted later by a dedicated kernel thread (cleaner kthread) which is woke up at the next transaction commit.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot metadata qgroup log` declares tags `auto quick snapshot metadata qgroup log`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `$XFS_IO_PROG -f -s -c "pwrite -S 0xaa 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap`; `_btrfs subvolume delete $SCRATCH_MNT/snap`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/a`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foobar`; `md5sum $SCRATCH_MNT/foobar | _filter_scratch`; `_flakey_drop_and_remount`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot metadata qgroup log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available. Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
