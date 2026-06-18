# sources/test-tools/xfstests/tests/btrfs/124

## Purpose

`sources/test-tools/xfstests/tests/btrfs/124` is btrfs fstests case `124`. It targets multi-device or RAID volume behavior, balance relocation behavior. Source comments describe the scenario as: This test verify the RAID1 reconstruction on the reappeared device. By using the following steps: Initialize a RAID1 with some data Re-mount RAID1 degraded with dev2 missing and write up to half of the FS capacity. Save md5sum checkpoint1 Re-mount healthy RAID1 Let balance re-silver. Save md5sum checkpoint2 Re-mount RAID1 degraded with dev1 missing

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto replace volume balance raid` declares tags `auto replace volume balance raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_btrfs_forget_or_module_loadable`, `_require_non_zoned_device "$dev1"`, `_require_non_zoned_device "$dev2"`, `_notrun "Smallest dev size $max_fs_sz, Need at least 2G"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_btrfs_rescan_devices`; `_require_scratch_dev_pool 2`; `_test_unmount`; `_require_btrfs_forget_or_module_loadable`; `_require_non_zoned_device "$dev1"`; `_require_non_zoned_device "$dev2"`; `_test_mount`; `_scratch_mount >> $seqres.full 2>&1`; `_mount -o degraded $dev1 $SCRATCH_MNT >>$seqres.full 2>&1`; `checkpoint1=\`md5sum $SCRATCH_MNT/tf2\``; `echo "Inital sum does not match with after balance"`; `if [ "$checkpoint1" != "$checkpoint3" ]; then`; `echo $checkpoint3`; `echo "Inital sum does not match with data on dev2 written by balance"`; `$UMOUNT_PROG $dev2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto replace volume balance raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
