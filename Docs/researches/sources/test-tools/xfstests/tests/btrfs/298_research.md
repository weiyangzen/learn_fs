# sources/test-tools/xfstests/tests/btrfs/298

## Purpose
Check if the device scan registers for a single-device seed and drops it from the kernel if it is eventually marked as non-seed. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick seed`. Requirement and capability gates: line 13: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 14: `_require_command "$WIPEFS_PROG" wipefs`; line 15: `_require_scratch_dev_pool 2`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 13: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 14: `_require_command "$WIPEFS_PROG" wipefs`; line 15: `_require_scratch_dev_pool 2`; line 16: `_scratch_dev_pool_get 1`; line 22: `echo "#setup seed sprout device" >> $seqres.full`; line 23: `_scratch_mkfs "-b 300M" >> $seqres.full 2>&1 || _fail "Fail to make SCRATCH_DEV with -b 300M"`; line 25: `$BTRFS_TUNE_PROG -S 1 $SCRATCH_DEV`; line 26: `_scratch_mount >> $seqres.full 2>&1`; line 27: `$BTRFS_UTIL_PROG device add $SPARE_DEV $SCRATCH_MNT >> $seqres.full`; line 28: `_scratch_unmount`; line 29: `$BTRFS_UTIL_PROG device scan --forget`; line 31: `echo "#Scan seed device and check using mount" >> $seqres.full`; line 32: `$BTRFS_UTIL_PROG device scan $SCRATCH_DEV >> $seqres.full`; line 33: `_mount $SPARE_DEV $SCRATCH_MNT`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick seed`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, btrfstune. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 298 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
