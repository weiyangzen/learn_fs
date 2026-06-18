# sources/test-tools/xfstests/tests/btrfs/185

## Purpose

`sources/test-tools/xfstests/tests/btrfs/185` is btrfs fstests case `185`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Fuzzy test for FS image duplication. Could be fixed by a9261d4125c9 ("btrfs: harden agaist duplicate fsid on scanned devices") Original device is mounted, scan of its clone must not alter the filesystem device path Original device scan should be successful

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest volume auto quick` declares tags `volume auto quick`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `$UMOUNT_PROG $mnt > /dev/null 2>&1`; `rm -rf $mnt > /dev/null 2>&1`; `rm -f $tmp.*`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `"btrfs: harden agaist duplicate fsid on scanned devices"`; `device_1=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `device_2=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `echo device_1=$device_1 device_2=$device_2 >> $seqres.full`; `_mkfs_dev $device_1`; `_mount $device_1 $mnt`; `skip=$sb_bytenr count=4096 > /dev/null 2>&1`; `$BTRFS_UTIL_PROG device scan $device_2 >> $seqres.full 2>&1`; `$BTRFS_UTIL_PROG device scan $device_1 >> $seqres.full 2>&1`; `_fail "if it fails here, then it means subvolume mount at boot may fail "\`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `volume auto quick` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
