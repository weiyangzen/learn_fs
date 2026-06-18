# sources/test-tools/xfstests/tests/btrfs/197

## Purpose

`sources/test-tools/xfstests/tests/btrfs/197` is btrfs fstests case `197`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test stale and alien btrfs-device in the fs devices list. Bug fixed in the kernel patch: btrfs: include non-missing as a qualifier for the latest_bdev btrfs: remove identified alien btrfs device in open_fs_devices We require at least one raid setup, raid1 is the easiest, use this to gate on wether or not we run this test Make device # 2 an alien btrfs device for the raid created above by adding it to the $TEST_DIR/$seq.mnt don't test with the first device as auto fs check (_check_scratch_fs) picks the first device

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume raid` declares tags `auto quick volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter.btrfs`; requirements: `_require_test`, `_require_scratch`, `_require_scratch_dev_pool 5`, `_require_btrfs_raid_type raid1`; local shell helpers: `_cleanup()`, `workout()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `$UMOUNT_PROG $TEST_DIR/$seq.mnt >/dev/null 2>&1`; `rm -rf $TEST_DIR/$seq.mnt`; `rm -f $tmp.*`; `_require_scratch`; `_require_scratch_dev_pool 5`; `device_nr=$2`; `_scratch_dev_pool_get $device_nr`; `_mount $SPARE_DEV $TEST_DIR/$seq.mnt`; `$BTRFS_UTIL_PROG device add -f "${SCRATCH_DEV_NAME[1]}" "$TEST_DIR/$seq.mnt" >> \`; `_mount -o degraded ${SCRATCH_DEV_NAME[0]} $SCRATCH_MNT`; `grep -q "${SCRATCH_DEV_NAME[1]}" $tmp.output && _fail "found stale device"`; `_scratch_dev_pool_put`; `workout "raid1" "2"`; `workout "raid5" "3"`; `workout "raid6" "4"`; `workout "raid10" "4"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
