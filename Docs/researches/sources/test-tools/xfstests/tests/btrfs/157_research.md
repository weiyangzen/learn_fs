# sources/test-tools/xfstests/tests/btrfs/157

## Purpose

`sources/test-tools/xfstests/tests/btrfs/157` is btrfs fstests case `157`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: The test case is to reproduce a bug in raid6 reconstruction process that would end up with read failure if there is data corruption on two disks in the same horizontal stripe, e.g.  due to bitrot. The bug happens when a) all disks are good to read, b) there is corrupted data on two disks in the same horizontal stripe due to something like bitrot, c) when rebuilding data after crc fails, btrfs is not able to tell whether other copies are good or corrupted because btrfs doesn't have crc for unallocated blocks.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick raid read_repair` declares tags `auto quick raid read_repair`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`, `_require_scratch_dev_pool 4`, `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_raid_type raid6`; local shell helpers: `get_physical()`, `get_devid()`, `get_device_path()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_btrfs_no_nodatacow`; `_require_btrfs_no_nodatasum`; `_require_scratch_dev_pool 4`; `_require_btrfs_command inspect-internal dump-tree`; `_require_btrfs_raid_type raid6`; `get_device_path()`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa 0 128K" -c "fsync" \`; `devpath0=$(get_device_path $devid0)`; `devpath1=$(get_device_path $devid1)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xbb $phy0 64K" $devpath0 > /dev/null`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xbb $phy1 64K" $devpath1 > /dev/null`; `echo "step 3......repair the bitrot" >> $seqres.full`; `od -x -j 64K $SCRATCH_MNT/foobar`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick raid read_repair` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
