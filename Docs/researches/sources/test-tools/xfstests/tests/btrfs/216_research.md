# sources/test-tools/xfstests/tests/btrfs/216

## Purpose

`sources/test-tools/xfstests/tests/btrfs/216` is btrfs fstests case `216`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test if the show_devname() returns sprout device instead of seed device. check if the show_devname() returns the sprout device instead of seed device.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick seed` declares tags `auto quick seed`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `"btrfs: don't traverse into the seed devices in show_devname"`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `seed=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `sprout=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `_mkfs_dev $seed`; `_mount $seed $SCRATCH_MNT >> $seqres.full 2>&1`; `cat /proc/self/mounts | grep $seed >> $seqres.full`; `$BTRFS_UTIL_PROG device add -f $sprout $SCRATCH_MNT >> $seqres.full`; `cat /proc/self/mounts | grep $sprout >> $seqres.full`; `dev=$(grep $SCRATCH_MNT /proc/self/mounts | $AWK_PROG '{print $1}')`; `if [ "$sprout" != "$dev" ]; then`; `echo "Unexpected device: $dev, expected $sprout"`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick seed` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
