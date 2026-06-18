# sources/test-tools/xfstests/tests/btrfs/270

## Purpose
Regression test for btrfs buffered read repair of compressed data. Create a file with all data being compressed success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick read_repair compress raid`. Requirement and capability gates: line 14: `_require_scratch`; line 15: `_require_btrfs_command inspect-internal dump-tree`; line 16: `_require_non_zoned_device "${SCRATCH_DEV}" # no overwrites on zoned devices`; line 17: `_require_scratch_dev_pool 2`. Local helper surface: `get_physical()` (line 20), `get_devid()` (line 29), `get_device_path()` (line 38). Important command/API calls include line 14: `_require_scratch`; line 15: `_require_btrfs_command inspect-internal dump-tree`; line 16: `_require_non_zoned_device "${SCRATCH_DEV}" # no overwrites on zoned devices`; line 17: `_require_scratch_dev_pool 2`; line 18: `_scratch_dev_pool_get 2`; line 24: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 3 $SCRATCH_DEV | grep $logical -A 6 | $AWK_PROG "(\$1 ~ /stripe/ && \$3 ~ /devid/ && \$2 ~ /$stripe/) { print \$6 }"`; line 33: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 3 $SCRATCH_DEV | grep $logical -A 6 | $AWK_PROG "(\$1 ~ /stripe/ && \$3 ~ /devid/ && \$2 ~ /$stripe/) { print \$4 }"`; line 38: `get_device_path()`; line 46: `_check_minimal_fs_size $(( 1024 * 1024 * 1024 ))`; line 47: `_scratch_pool_mkfs "-d raid1 -b 1G" >>$seqres.full 2>&1`; line 48: `_scratch_mount -ocompress`; line 51: `$XFS_IO_PROG -f -c "pwrite -S 0xaa -W -b 128K 0 128K" "$SCRATCH_MNT/foobar" | _filter_xfs_io_offset`; line 54: `logical_in_btrfs=$(_btrfs_get_first_logical $SCRATCH_MNT/foobar)`; line 55: `physical=$(get_physical ${logical_in_btrfs} 1)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick read_repair compress raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 270 | step 1......mkfs.btrfs | wrote 131072/131072 bytes | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | step 2......corrupt file extent | step 3......repair the bad copy | step 4......check if the repair worked`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
