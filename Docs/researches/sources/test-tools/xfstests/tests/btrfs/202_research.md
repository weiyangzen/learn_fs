# sources/test-tools/xfstests/tests/btrfs/202

## Purpose

`sources/test-tools/xfstests/tests/btrfs/202` is btrfs fstests case `202`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: Regression test for fix "btrfs: fix invalid removal of root ref" Create a subvol b under a and then snapshot a into c.  This create's a stub entry in c for b because c doesn't have a reference for b. But when we rename b c/foo it creates a ref for b in c.  However if we go to remove c/b btrfs used to depend on not finding the root ref to handle the unlink properly, but we now have a ref for that root.  We also had a bug that would allow us to remove mis-matched refs if the keys matched, so we'd end up removing too many entries which would cause a transaction abort. Need the dummy entry created so that we get the invalid removal when we rmdir

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick subvol snapshot` declares tags `auto quick subvol snapshot`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/a | _filter_scratch`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/a/b | _filter_scratch`; `_btrfs subvolume snapshot $SCRATCH_MNT/a $SCRATCH_MNT/c`; `mkdir $SCRATCH_MNT/c/foo`; `mv $SCRATCH_MNT/a/b $SCRATCH_MNT/c/foo`; `rm -rf $SCRATCH_MNT/*`; `touch $SCRATCH_MNT/blah`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick subvol snapshot` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
