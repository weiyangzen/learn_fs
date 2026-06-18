# sources/test-tools/xfstests/tests/btrfs/215

## Purpose

`sources/test-tools/xfstests/tests/btrfs/215` is btrfs fstests case `215`. It targets checksum, scrub, or read-repair paths. Source comments describe the scenario as: Test that reading corrupted files would correctly increment device status counters. This is fixed by the following linux kernel commit: 814723e0a55a ("btrfs: increment device corruption error in case of checksum error") No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. Overwriting data is forbidden on a zoned block device We need to ensure a fixed amount of written blocks to trigger a specific number of read errors and we corrupt by writing directly to the device, so skip if compression is enabled. disable freespace inode to ensure file is the first thing in the data

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick read_repair` declares tags `auto quick read_repair`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`, `_require_non_zoned_device $SCRATCH_DEV`, `_require_no_compress`, `_notrun "this test doesn't support sectorsize $blocksize with page size $pagesize yet"`, `_notrun "bdi link not found"`; local shell helpers: `get_physical()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 3 $SCRATCH_DEV | \`; `_require_scratch`; `_require_btrfs_no_nodatacow`; `_require_btrfs_no_nodatasum`; `_require_non_zoned_device $SCRATCH_DEV`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `uuid=$(findmnt -n -o UUID "$SCRATCH_MNT")`; `$XFS_IO_PROG -d -f -c "pwrite -S 0xbb -b $filesize 0 $filesize" "$SCRATCH_MNT/foobar" > /dev/null`; `$XFS_IO_PROG -d -c "pwrite -S 0xaa -b $pagesize $physical_extent $((4 * $pagesize))" $SCRATCH_DEV > /dev/null`; `_scratch_mount`; `echo 0 > /sys/fs/btrfs/$uuid/bdi/read_ahead_kb`; `$XFS_IO_PROG -c "pread -b $filesize 0 $filesize" "$SCRATCH_MNT/foobar" > /dev/null 2>&1`; `errs=$($BTRFS_UTIL_PROG device stats $SCRATCH_DEV | $AWK_PROG '/corruption_errs/ { print $2 }')`; `$XFS_IO_PROG -d -c "pread -b $filesize 0 $filesize" "$SCRATCH_MNT/foobar" > /dev/null 2>&1`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick read_repair` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. `btrfs device stats` counters are inspected for expected readable/corruption accounting.
