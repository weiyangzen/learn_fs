# sources/test-tools/xfstests/tests/btrfs/271

## Purpose
Test btrfs write error propagation and reporting on the raid1 profile. btrfs counts errors per IO, assuming the data is merged that'll be 1 IO, then the log tree block and then the log root tree block and then the super block. We should see at least 4 failed IO's, but with subpage blocksize we could see more if the log blocks end up on the same page, or if the data IO gets split at all. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick raid`. Requirement and capability gates: line 15: `_require_scratch`; line 16: `_require_fail_make_request`; line 17: `_require_scratch_dev_pool 2`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 15: `_require_scratch`; line 16: `_require_fail_make_request`; line 17: `_require_scratch_dev_pool 2`; line 18: `_scratch_dev_pool_get 2`; line 20: `_check_minimal_fs_size $(( 1024 * 1024 * 1024 ))`; line 21: `_scratch_pool_mkfs "-m raid1 -d raid1 -b 1G" >> $seqres.full 2>&1`; line 23: `_scratch_mount`; line 31: `$XFS_IO_PROG -f -c "pwrite -W -S 0xaa 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 39: `errs=$($BTRFS_UTIL_PROG device stats $SCRATCH_DEV | $AWK_PROG '/write_io_errs/ { print $2 }')`; line 46: `$XFS_IO_PROG -c "pread -v 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io_offset`; line 51: `$XFS_IO_PROG -f -c "pwrite -W -S 0xbb 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 57: `_scratch_dev_pool_put`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 271 | Allow global fail_make_request feature | Step 1: writing with one failing mirror: | wrote 8192/8192 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Step 2: verify that the data reads back fine: | XXXXXXXX:  aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa  ................ | XXXXXXXX:  aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa  ................ | ... (523 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
