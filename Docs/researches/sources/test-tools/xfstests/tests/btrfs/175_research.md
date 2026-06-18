# sources/test-tools/xfstests/tests/btrfs/175

## Purpose

`sources/test-tools/xfstests/tests/btrfs/175` is btrfs fstests case `175`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test swap file activation on multiple devices. Each device is only 1 GB, so 1.5 GB must be split across multiple devices. Create the swap file, then add the device. That way we know it's all on one device.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap volume raid` declares tags `auto quick swap volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_scratch_swapfile`; local shell helpers: `cycle_swapfile()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_require_scratch_swapfile`; `_check_minimal_fs_size $((1024 * 1024 * 1024))`; `swapon "$SCRATCH_MNT/swap" 2>&1 | _filter_scratch`; `_scratch_pool_mkfs -d raid1 -m raid1 >> $seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_scratch_pool_mkfs -d dup -m dup >> $seqres.full 2>&1`; `echo "Single on multiple devices"`; `_scratch_pool_mkfs -d single -m raid1 -b $((1024 * 1024 * 1024)) >> $seqres.full 2>&1`; `echo "Single on one device"`; `_scratch_mkfs >> $seqres.full 2>&1`; `scratch_dev2="$(echo "${SCRATCH_DEV_POOL}" | $AWK_PROG '{ print $2 }')"`; `$BTRFS_UTIL_PROG device add -f "$scratch_dev2" "$SCRATCH_MNT" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
