# sources/test-tools/xfstests/tests/btrfs/218

## Purpose

`sources/test-tools/xfstests/tests/btrfs/218` is btrfs fstests case `218`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Make a seed device, add a sprout to it, and then make sure we can still read the device stats for both devices after we remount with the new sprout device. Create the seed device Mount the seed device and add the rw device Now remount, validate the device stats do not fail

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume` declares tags `auto quick volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_test`, `_require_scratch_dev_pool 2`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `"btrfs: init device stats for seed devices"`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `dev_seed=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `dev_sprout=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `_mkfs_dev $dev_seed`; `_mount $dev_seed $SCRATCH_MNT`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foo > /dev/null`; `$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT | \`; `_filter_btrfs_filesystem_show`; `_scratch_unmount`; `_mount -o ro $dev_seed $SCRATCH_MNT`; `_btrfs device add -f $dev_sprout $SCRATCH_MNT >> $seqres.full`; `$BTRFS_UTIL_PROG device stats $SCRATCH_MNT | _filter_scratch_pool`; `_mount $dev_sprout $SCRATCH_MNT`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `btrfs device stats` counters are inspected for expected readable/corruption accounting.
