# sources/test-tools/xfstests/tests/btrfs/163

## Purpose

`sources/test-tools/xfstests/tests/btrfs/163` is btrfs fstests case `163`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test case to verify that a sprouted device can be replaced Create a seed device Create a sprout device Remount RW Run device replace on the sprout device Depends on the kernel patch c6a5d954950c btrfs: fail replace of seed device

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume seed remount` declares tags `auto quick volume seed remount`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_command "$BTRFS_TUNE_PROG" btrfstune`, `_require_scratch_dev_pool 3`, `_require_btrfs_forget_or_module_loadable`; local shell helpers: `_cleanup()`, `create_seed()`, `add_sprout()`, `replace_sprout()`, `seed_is_mountable()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_btrfs_rescan_devices`; `_require_scratch_dev_pool 3`; `_require_btrfs_forget_or_module_loadable`; `_scratch_dev_pool_get 3`; `dev_replace_tgt=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $3}')`; `run_check _mount $dev_seed $SCRATCH_MNT`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 4M" $SCRATCH_MNT/foobar >\`; `_btrfs device add -f $dev_sprout $SCRATCH_MNT >>\`; `_mount -o remount,rw $dev_sprout $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xcd 0 4M" $SCRATCH_MNT/foobar2 >\`; `od -x $SCRATCH_MNT/foobar2`; `seed_is_mountable()`; `replace_sprout`; `seed_is_mountable`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume seed remount` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
