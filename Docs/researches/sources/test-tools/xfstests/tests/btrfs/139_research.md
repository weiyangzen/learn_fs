# sources/test-tools/xfstests/tests/btrfs/139

## Purpose

`sources/test-tools/xfstests/tests/btrfs/139` is btrfs fstests case `139`. It targets quota-group accounting and limits. Source comments describe the scenario as: Check if btrfs quota limits are not reached when you constantly create and delete files within the exclusive qgroup limits. Finally we create files to exceed the quota. We at least need 2GB of free space on $SCRATCH_DEV This test requires specific data space usage, skip if we have compression enabled. Write and delete files within 1G limits, multiple times Exceed the limits here

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto qgroup limit` declares tags `auto qgroup limit`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_size $((2 * 1024 * 1024))`, `_require_no_compress`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_size $((2 * 1024 * 1024))`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `SUBVOL=$SCRATCH_MNT/subvol`; `_btrfs subvolume create $SUBVOL`; `_btrfs quota enable $SCRATCH_MNT`; `_qgroup_rescan $SCRATCH_MNT`; `_btrfs qgroup limit -e 1G $SUBVOL`; `$XFS_IO_PROG -f -c "pwrite 0 4m" $SUBVOL/file_$j > /dev/null`; `rm -f $SUBVOL/file*`; `$XFS_IO_PROG -f -c "pwrite 0 128m" $SUBVOL/file_$j 2>&1 | _filter_xfs_io | _filter_xfs_io_error`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto qgroup limit` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
