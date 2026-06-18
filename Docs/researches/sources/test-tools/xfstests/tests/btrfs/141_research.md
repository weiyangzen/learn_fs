# sources/test-tools/xfstests/tests/btrfs/141

## Purpose

`sources/test-tools/xfstests/tests/btrfs/141` is btrfs fstests case `141`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Regression test for btrfs buffered read's repair during read. Commit 20a7db8ab3f2 ("btrfs: add dummy callback for readpage_io_failed and drop checks") introduced the regression. The upstream fix is Commit 9d0d1c8b1c9d ("Btrfs: bring back repair during read") No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. step 1, create a raid1 btrfs which contains one 128k file. make sure data is written to the start position of the data chunk step 2, corrupt the first 64k of one copy (on SCRATCH_DEV which is the first

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick read_repair raid` declares tags `auto quick read_repair raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`, `_require_scratch_dev_pool 2`, `_require_btrfs_command inspect-internal dump-tree`; local shell helpers: `get_physical()`, `get_devid()`, `get_device_path()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_btrfs_no_nodatacow`; `_require_btrfs_no_nodatasum`; `_require_scratch_dev_pool 2`; `_require_btrfs_command inspect-internal dump-tree`; `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 3 $SCRATCH_DEV | \`; `get_device_path()`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" |\`; `devpath=$(get_device_path ${devid})`; `$XFS_IO_PROG -c "pread -v -b 512 $physical 512" $devpath |\`; `$XFS_IO_PROG -d -c "pwrite -S 0xbb -b 64K $physical 64K" $devpath > /dev/null`; `_btrfs_buffered_read_on_mirror 1 2 "$SCRATCH_MNT/foobar" 0 128K`; `finalcsum=$(_md5_checksum $final)`; `rm -f $final`; `_scratch_dev_pool_put`; `[ "$origcsum" == "$finalcsum" ] || _fail "repair failed, csums don't match"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick read_repair raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
