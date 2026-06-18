# sources/test-tools/xfstests/tests/btrfs/249

## Purpose
Validate if the command 'btrfs filesystem usage' works with missing seed device Steps: Create a degraded raid1 seed device Create a sprout filesystem (an rw device on top of a seed device) Dump 'btrfs filesystem usage', check it didn't fail use the scratch devices as seed devices use the spare device as a sprout device create raid1 seed filesystem. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick seed volume raid`. Requirement and capability gates: line 19: `_require_scratch_dev_pool 3`; line 20: `_require_command "$WIPEFS_PROG" wipefs`; line 21: `_require_btrfs_forget_or_module_loadable`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 19: `_require_scratch_dev_pool 3`; line 20: `_require_command "$WIPEFS_PROG" wipefs`; line 21: `_require_btrfs_forget_or_module_loadable`; line 22: `_wants_kernel_commit a26d60dedf9a "btrfs: sysfs: add devinfo/fsid to retrieve actual fsid from the device"`; line 24: `_fixed_by_git_commit btrfs-progs 32c2e57c65b9 "btrfs-progs: read fsid from the sysfs in device_is_seed"`; line 27: `_scratch_dev_pool_get 2`; line 37: `_scratch_pool_mkfs "-draid1 -mraid1" >> $seqres.full 2>&1`; line 38: `$BTRFS_TUNE_PROG -S 1 $seed_dev1`; line 40: `_btrfs_forget_or_module_reload`; line 41: `_mount -o degraded $seed_dev2 $SCRATCH_MNT >> $seqres.full 2>&1`; line 44: `$BTRFS_UTIL_PROG device add -f $SPARE_DEV $SCRATCH_MNT >> $seqres.full 2>&1`; line 47: `$BTRFS_UTIL_PROG filesystem usage $SCRATCH_MNT >> $seqres.full`; line 51: `_fail "FAILED: btrfs filesystem usage, ret $ret. Check btrfs.ko and btrfs-progs version."`; line 54: `_scratch_unmount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick seed volume raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, btrfstune. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 249 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
