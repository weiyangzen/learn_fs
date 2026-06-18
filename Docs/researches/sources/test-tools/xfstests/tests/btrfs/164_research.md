# sources/test-tools/xfstests/tests/btrfs/164

## Purpose

`sources/test-tools/xfstests/tests/btrfs/164` is btrfs fstests case `164`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test case to verify that a seed device can be deleted Create a seed device Create a sprout device Remount RW Run device delete on the seed device

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume remount` declares tags `auto quick volume remount`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`; requirements: `_require_btrfs_forget_or_module_loadable`, `_require_scratch_dev_pool 2`; local shell helpers: `_cleanup()`, `create_seed()`, `add_sprout()`, `delete_seed()`, `seed_is_mountable()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_btrfs_rescan_devices`; `_require_btrfs_forget_or_module_loadable`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `run_check _mount $dev_seed $SCRATCH_MNT`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 256K" $SCRATCH_MNT/foobar >\`; `_btrfs device add -f $dev_sprout $SCRATCH_MNT >>\`; `run_check mount -o rw,remount $dev_seed $SCRATCH_MNT`; `_btrfs device delete $dev_seed $SCRATCH_MNT`; `_btrfs_forget_or_module_reload`; `run_check _mount $dev_sprout $SCRATCH_MNT`; `seed_is_mountable()`; `seed_is_mountable`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume remount` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
