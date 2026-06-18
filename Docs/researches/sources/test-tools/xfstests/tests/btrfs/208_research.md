# sources/test-tools/xfstests/tests/btrfs/208

## Purpose

`sources/test-tools/xfstests/tests/btrfs/208` is btrfs fstests case `208`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: Test subvolume deletion using the subvolume id, even when the subvolume in question is in a different mount space. Test creating a normal subvolumes Delete the subvolume subvol1, and list the remaining two subvolumes Now we mount the subvol2, which makes subvol3 not accessible for this mount point, but we should be able to delete it using it's subvolume id now mount the rootfs Delete the subvol2

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick subvol` declares tags `auto quick subvol`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_scratch`, `_require_btrfs_command subvolume delete --subvolid`; local shell helpers: `_delete_and_list()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_command subvolume delete --subvolid`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `SUBVOLID=$(_btrfs_get_subvolid $SCRATCH_MNT "$subvol_name")`; `$BTRFS_UTIL_PROG subvolume delete --subvolid $SUBVOLID $SCRATCH_MNT | _filter_btrfs_subvol_delete`; `$BTRFS_UTIL_PROG subvolume list $SCRATCH_MNT | $AWK_PROG '{ print $NF }'`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol1 | _filter_scratch`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol2 | _filter_scratch`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol3 | _filter_scratch`; `echo "Current subvolume ids:"`; `_delete_and_list subvol1 "After deleting one subvolume:"`; `_scratch_unmount`; `$MOUNT_PROG -o subvol=subvol2 $SCRATCH_DEV $SCRATCH_MNT`; `_delete_and_list subvol3 "Last remaining subvolume:"`; `_delete_and_list subvol2 "All subvolumes removed."`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick subvol` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
