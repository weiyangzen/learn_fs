# sources/test-tools/xfstests/tests/btrfs/121

## Purpose

`sources/test-tools/xfstests/tests/btrfs/121` is btrfs fstests case `121`. It targets subvolume/snapshot metadata, quota-group accounting and limits. Source comments describe the scenario as: Test that an invalid parent qgroup does not cause snapshot create to force the FS readonly. This issue is fixed by the following btrfs patch: [PATCH] btrfs: handle non-fatal errors in btrfs_qgroup_inherit() http://thread.gmane.org/gmane.comp.file-systems.btrfs/54755 The qgroup '1/10' does not exist. The kernel should either gives an error (newer kernel with invalid qgroup detection) or ignore it (older kernel with above fix). Either way, we just ignore the output completely, and we will check if the fs is still RW later.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot qgroup` declares tags `auto quick snapshot qgroup`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs >/dev/null`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG subvolume snapshot -i 1/10 $SCRATCH_MNT $SCRATCH_MNT/snap1 >> $seqres.full 2>&1`; `touch $SCRATCH_MNT/foobar`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot qgroup` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
