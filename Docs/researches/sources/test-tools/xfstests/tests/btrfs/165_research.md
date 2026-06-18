# sources/test-tools/xfstests/tests/btrfs/165

## Purpose

`sources/test-tools/xfstests/tests/btrfs/165` is btrfs fstests case `165`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: QA test that checks rmdir(2) works for subvolumes like ordinary directories. This behavior has been restricted long time but becomes allowed by kernel commit a79a464d5675 ("btrfs: Allow rmdir(2) to delete an empty subvolume") Check that an empty subvolume can be deleted by rmdir Check that non-empty subvolume cannot be deleted by rmdir Check that read-only empty subvolume can be deleted by rmdir Check that the default subvolume cannot be deleted by rmdir Check that subvolume stub (created by snapshot) can be deleted by rmdir (Note: this has been always allowed) Check that rm -r works for both non-snapshot subvolume and snapshot

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick subvol` declares tags `auto quick subvol`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_fs_feature "rmdir_subvol"`; local shell helpers: `create_subvol()`, `create_snapshot()`, `rmdir_subvol()`, `rm_r_subvol()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `$BTRFS_UTIL_PROG subvolume create $1 >> $seqres.full 2>&1`; `create_snapshot()`; `$BTRFS_UTIL_PROG subvolume snapshot $@ >> $seqres.full 2>&1`; `rm -r $1 >> $seqres.full 2>&1`; `_require_scratch`; `_scratch_mount`; `echo "rmdir should delete an empty subvolume"`; `echo "rmdir should fail for non-empty subvolume"`; `create_snapshot -r $SCRATCH_MNT/sub3 $SCRATCH_MNT/snap`; `echo "rmdir should delete a readonly empty subvolume"`; `$BTRFS_UTIL_PROG subvolume set-default $subvolid $SCRATCH_MNT \`; `create_snapshot $SCRATCH_MNT/sub7 $SCRATCH_MNT/snap3`; `create_snapshot -r $SCRATCH_MNT/sub7 $SCRATCH_MNT/snap4`; `echo "rm -r should delete subvolumes recursively"`; `echo "rm -r should fail for non-empty readonly subvolume"`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT/snap4 ro false >> $seqres.full 2>&1`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick subvol` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
