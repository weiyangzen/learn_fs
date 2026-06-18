# sources/test-tools/xfstests/tests/btrfs/225

## Purpose
Test for seed device-delete on a sprouted FS. Steps: Create a seed FS. Add a RW device to make it sprout FS and then delete the seed device. Override the default cleanup function. Mount the seed device and add the rw device Now remount success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume seed`. Requirement and capability gates: line 28: `_require_test`; line 29: `_require_scratch_dev_pool 2`; line 30: `_require_btrfs_forget_or_module_loadable`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 20: `rm -f $tmp.*`; line 21: `_btrfs_rescan_devices`; line 26: `_fixed_by_kernel_commit b5ddcffa3777 "btrfs: fix put of uninitialized kobject after seed device delete"`; line 28: `_require_test`; line 29: `_require_scratch_dev_pool 2`; line 30: `_require_btrfs_forget_or_module_loadable`; line 32: `_scratch_dev_pool_get 2`; line 38: `_mount $seed $SCRATCH_MNT`; line 40: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foo > /dev/null`; line 41: `_scratch_unmount`; line 42: `$BTRFS_TUNE_PROG -S 1 $seed`; line 45: `_mount -o ro $seed $SCRATCH_MNT`; line 46: `$BTRFS_UTIL_PROG device add -f $sprout $SCRATCH_MNT >> $seqres.full`; line 50: `_mount $sprout $SCRATCH_MNT`. It documents fixed kernel commit context at line 26: `_fixed_by_kernel_commit b5ddcffa3777 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume seed`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, btrfstune. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 225 | --- before delete ---- | 0000000 abab abab abab abab abab abab abab abab | * | 4000000 | 0000000 cdcd cdcd cdcd cdcd cdcd cdcd cdcd cdcd | * | 4000000 | ... (15 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
