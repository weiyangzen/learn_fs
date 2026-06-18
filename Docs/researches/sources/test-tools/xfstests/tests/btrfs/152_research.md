# sources/test-tools/xfstests/tests/btrfs/152

## Purpose

`sources/test-tools/xfstests/tests/btrfs/152` is btrfs fstests case `152`. It targets quota-group accounting and limits, send/receive stream correctness. Source comments describe the scenario as: Test that incremental send/receive operations don't corrupt metadata when qgroups are enabled. Enable quotas Create 2 source and 4 destination subvolumes Create base snapshots and send them Now do 10 loops of concurrent incremental send/receives

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick metadata qgroup send` declares tags `auto quick metadata qgroup send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/$subvol | _filter_scratch`; `mkdir $SCRATCH_MNT/subvol{1,2}/.snapshots`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/subvol1 $SCRATCH_MNT/subvol1/.snapshots/1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/subvol2 $SCRATCH_MNT/subvol2/.snapshots/1`; `$BTRFS_UTIL_PROG send $SCRATCH_MNT/subvol1/.snapshots/1 2> /dev/null | \`; `$BTRFS_UTIL_PROG receive $SCRATCH_MNT/${recv} | _filter_scratch`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/subvol1 \`; `($BTRFS_UTIL_PROG send -p $SCRATCH_MNT/subvol2/.snapshots/${prev} \`; `$SCRATCH_MNT/subvol2/.snapshots/${curr} 2> /dev/null | \`; `$BTRFS_UTIL_PROG receive $SCRATCH_MNT/recv2_1) > /dev/null &`; `$BTRFS_UTIL_PROG receive $SCRATCH_MNT/recv2_2) > /dev/null &`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick metadata qgroup send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation. Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
