# sources/test-tools/xfstests/tests/btrfs/194

## Purpose

`sources/test-tools/xfstests/tests/btrfs/194` is btrfs fstests case `194`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test if btrfs can handle large device ids. The regression is introduced by kernel commit ab4ba2e13346 ("btrfs: tree-checker: Verify dev item"). The fix is titled: "btrfs: tree-checker: Fix wrong check on max devid" Here we use 4k node size to reduce runtime (explained near _scratch_mkfs call) To use the minimal node size (4k) we need 4K page size. The wrong check limit is based on the max item size (BTRFS_MAX_DEVS() macro), and max item size is based on node size, so smaller node size will result much shorter runtime. So here we use minimal node size (4K) to reduce runtime. For 4k nodesize, the wrong limit is calculated by:

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto volume` declares tags `auto volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_btrfs_support_sectorsize 4096`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `_require_btrfs_support_sectorsize 4096`; `device_1=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `device_2=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `echo device_1=$device_1 device_2=$device_2 >> $seqres.full`; `_scratch_mkfs -n 4k -s 4k >> $seqres.full`; `_scratch_mount`; `$BTRFS_UTIL_PROG device add -f $device_2 $SCRATCH_MNT >> $seqres.full`; `$BTRFS_UTIL_PROG device del $device_1 $SCRATCH_MNT`; `$BTRFS_UTIL_PROG device add -f $device_1 $SCRATCH_MNT >> $seqres.full`; `$BTRFS_UTIL_PROG device del $device_2 $SCRATCH_MNT`; `done | grep -v 'Resetting device zone'`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
