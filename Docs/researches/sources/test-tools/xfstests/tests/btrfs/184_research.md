# sources/test-tools/xfstests/tests/btrfs/184

## Purpose

`sources/test-tools/xfstests/tests/btrfs/184` is btrfs fstests case `184`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Verify that when a device is removed from a multi-device filesystem its superblock copies are correctly deleted Explicitly use raid0 mode to ensure at least one of the devices can be removed. pick last dev in the list

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume raid` declares tags `auto quick volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_scratch_dev_pool 2`, `_require_btrfs_command inspect-internal dump-super`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_dev_pool 2`; `_require_btrfs_command inspect-internal dump-super`; `_scratch_dev_pool_get 2`; `_scratch_pool_mkfs "-d raid0 -m raid0" >> $seqres.full 2>&1 || _fail "mkfs failed"`; `_scratch_mount`; `dev_del=\`echo ${SCRATCH_DEV_POOL} | $AWK_PROG '{print $NF}'\``; `$BTRFS_UTIL_PROG device delete $dev_del $SCRATCH_MNT || _fail "btrfs device delete failed"`; `output=$($BTRFS_UTIL_PROG inspect-internal dump-super -s $i $dev_del 2>&1)`; `$BTRFS_UTIL_PROG inspect-internal dump-super -s $i $dev_del 2>&1 | grep -q "bad magic"`; `_scratch_unmount`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
