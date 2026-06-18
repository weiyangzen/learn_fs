# sources/test-tools/xfstests/tests/btrfs/248

## Purpose
Validate if the sysfs devinfo/<devid>/fsid behaves properly Steps: Create a sprout filesystem (an rw device on top of a seed device) Read the seed and sprout devices fsid from the superblock Validate with the sysfs fsid use the scratch device as a seed device use the spare device as a sprout device create seed device create a sprout device. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick seed volume`. Requirement and capability gates: line 17: `_require_test`; line 18: `_require_scratch_dev_pool 2`; line 19: `_require_btrfs_forget_or_module_loadable`; line 20: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 21: `_require_btrfs_command inspect-internal dump-super`; line 22: `_require_btrfs_sysfs_fsid`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 17: `_require_test`; line 18: `_require_scratch_dev_pool 2`; line 19: `_require_btrfs_forget_or_module_loadable`; line 20: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 21: `_require_btrfs_command inspect-internal dump-super`; line 22: `_require_btrfs_sysfs_fsid`; line 24: `_scratch_dev_pool_get 1`; line 32: `_scratch_pool_mkfs >> $seqres.full 2>&1`; line 33: `$BTRFS_TUNE_PROG -S 1 $seed_dev`; line 34: `_scratch_mount >> $seqres.full 2>&1`; line 37: `$BTRFS_UTIL_PROG device add -f $SPARE_DEV $SCRATCH_MNT >> $seqres.full 2>&1`; line 38: `_scratch_unmount`; line 41: `seedfsid=$($BTRFS_UTIL_PROG inspect-internal dump-super $seed_dev |grep ^fsid | $AWK_PROG '{print $2}')`; line 43: `sproutfsid=$($BTRFS_UTIL_PROG inspect-internal dump-super $SPARE_DEV | grep ^fsid |$AWK_PROG '{print $2}')`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick seed volume`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, btrfstune. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 248 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
