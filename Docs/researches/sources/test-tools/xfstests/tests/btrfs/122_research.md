# sources/test-tools/xfstests/tests/btrfs/122

## Purpose

`sources/test-tools/xfstests/tests/btrfs/122` is btrfs fstests case `122`. It targets subvolume/snapshot metadata, quota-group accounting and limits. Source comments describe the scenario as: Test that qgroup counts are valid after snapshot creation. This has been broken in btrfs since Linux v4.1 First make some simple snapshots - the bug was initially reproduced like this This forces the fs tree out past level 0, adding at least one tree block which must be properly accounted for when we make our next snapshots. Snapshot twice. qgroup will be checked by fstest at _check_scratch_fs()

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot qgroup` declares tags `auto quick snapshot qgroup`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_qgroup_report`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_qgroup_report`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `mkdir "$SCRATCH_MNT/snaps"`; `_btrfs subvolume snapshot $SCRATCH_MNT "$SCRATCH_MNT/snaps/empty1"`; `_btrfs subvolume snapshot $SCRATCH_MNT "$SCRATCH_MNT/snaps/empty2"`; `mkdir "$SCRATCH_MNT/data"`; `$XFS_IO_PROG -f -c "pwrite 0 1M" "$SCRATCH_MNT/data/file$i" > /dev/null 2>&1`; `_btrfs subvolume snapshot $SCRATCH_MNT "$SCRATCH_MNT/snaps/snap1"`; `_btrfs subvolume snapshot $SCRATCH_MNT "$SCRATCH_MNT/snaps/snap2"`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot qgroup` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
