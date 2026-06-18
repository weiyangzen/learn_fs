# sources/test-tools/xfstests/tests/btrfs/176

## Purpose

`sources/test-tools/xfstests/tests/btrfs/176` is btrfs fstests case `176`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test device remove/replace with an active swap file. We check the filesystem manually because we move devices around. We know the swap file is on device 1 because we added device 2 after it was already created. Deleting/readding device 2 should still work. Deleting device 1 should work again after swapoff. Again, we know the swap file is on device 1. Replacing device 2 should still work. Replacing device 1 should work again after swapoff.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap volume` declares tags `auto quick swap volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 3`, `_require_scratch_swapfile`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 3`; `_require_scratch_swapfile`; `rm -f "${RESULT_DIR}/require_scratch"`; `scratch_dev1="$(echo "${SCRATCH_DEV_POOL}" | $AWK_PROG '{ print $1 }')"`; `scratch_dev2="$(echo "${SCRATCH_DEV_POOL}" | $AWK_PROG '{ print $2 }')"`; `echo "Remove device"`; `_scratch_mount`; `$BTRFS_UTIL_PROG device add -f "$scratch_dev2" "$SCRATCH_MNT" >> $seqres.full`; `$BTRFS_UTIL_PROG device delete "$scratch_dev1" "$SCRATCH_MNT" 2>&1 | grep -o "Text file busy"`; `$BTRFS_UTIL_PROG device delete "$scratch_dev2" "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG device delete "$scratch_dev1" "$SCRATCH_MNT"`; `_check_dev_fs "$scratch_dev2"`; `echo "Replace device"`; `$BTRFS_UTIL_PROG replace start -fB "$scratch_dev1" "$scratch_dev3" "$SCRATCH_MNT" 2>&1 | grep -o "Text file busy"`; `$BTRFS_UTIL_PROG replace start -fB "$scratch_dev2" "$scratch_dev3" "$SCRATCH_MNT" \`; `$BTRFS_UTIL_PROG replace start -fB "$scratch_dev1" "$scratch_dev2" "$SCRATCH_MNT" \`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
