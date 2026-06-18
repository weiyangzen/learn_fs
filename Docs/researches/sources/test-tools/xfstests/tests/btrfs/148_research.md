# sources/test-tools/xfstests/tests/btrfs/148

## Purpose

`sources/test-tools/xfstests/tests/btrfs/148` is btrfs fstests case `148`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Test that direct IO writes work on RAID5 and RAID6 filesystems. Now read back the same data, we expect to get what we wrote before.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick rw scrub raid` declares tags `auto quick rw scrub raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_scratch_dev_pool 4`, `_require_odirect`, `_require_btrfs_raid_type raid5`, `_require_btrfs_raid_type raid6`; local shell helpers: `test_direct_io_write()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_dev_pool 4`; `_require_btrfs_raid_type raid5`; `_require_btrfs_raid_type raid6`; `_scratch_dev_pool_get 4`; `_scratch_mount`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foo \`; `_scratch_cycle_mount`; `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`; `_scratch_unmount`; `test_direct_io_write "-m raid5 -d raid5"`; `test_direct_io_write "-m raid6 -d raid6"`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick rw scrub raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. A foreground scrub must complete without reported errors.
