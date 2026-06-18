# sources/test-tools/xfstests/tests/btrfs/151

## Purpose

`sources/test-tools/xfstests/tests/btrfs/151` is btrfs fstests case `151`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test if it's losing data chunk's raid profile after 'btrfs device remove'. The fix is Btrfs: avoid losing data raid profile when deleting a device We need exactly 3 disks to form a fixed stripe layout for this test. create raid1 for data we need an empty data chunk, so $(_btrfs_no_v1_cache_opt) is required. if data chunk is empty, 'btrfs device remove' can change raid1 to single. save btrfs filesystem df output for debug purpose

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume raid` declares tags `auto quick volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_scratch_dev_pool 3`, `_require_btrfs_dev_del_by_devid`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_dev_pool 3`; `_require_btrfs_dev_del_by_devid`; `_check_minimal_fs_size $(( 1024 * 1024 * 1024 ))`; `_scratch_dev_pool_get 3`; `_scratch_pool_mkfs "-d raid1 -b 1G" >> $seqres.full 2>&1`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$BTRFS_UTIL_PROG device delete 2 $SCRATCH_MNT >> $seqres.full 2>&1`; `$BTRFS_UTIL_PROG filesystem df $SCRATCH_MNT 2>&1 | \`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
