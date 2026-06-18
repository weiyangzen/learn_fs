# sources/test-tools/xfstests/tests/btrfs/238

## Purpose
Check seed device integrity after fstrim on the sprout device. Mount the seed device and add the rw device Now remount writeable sprout device, create some data and run fstrim Verify seed device is all ok success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics, discard/trim behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick seed trim`. Requirement and capability gates: line 16: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 17: `_require_fstrim`; line 18: `_require_scratch_dev_pool 2`; line 40: `_require_batched_discard $SCRATCH_MNT`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 14: `_fixed_by_kernel_commit 5e753a817b2d "btrfs: fix unmountable seed device after fstrim"`; line 16: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 17: `_require_fstrim`; line 18: `_require_scratch_dev_pool 2`; line 19: `_scratch_dev_pool_get 2`; line 25: `_mount $seed $SCRATCH_MNT`; line 27: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foo > /dev/null`; line 28: `_scratch_unmount`; line 29: `$BTRFS_TUNE_PROG -S 1 $seed`; line 32: `_mount $seed $SCRATCH_MNT 2>&1 | _filter_ro_mount | _filter_scratch`; line 33: `md5sum $SCRATCH_MNT/foo | _filter_scratch`; line 35: `$BTRFS_UTIL_PROG device add -f $sprout $SCRATCH_MNT >> $seqres.full`; line 39: `_mount $sprout $SCRATCH_MNT`; line 40: `_require_batched_discard $SCRATCH_MNT`. It documents fixed kernel commit context at line 14: `_fixed_by_kernel_commit 5e753a817b2d \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick seed trim`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, btrfstune, fstrim/discard support. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 238 | mount: device write-protected, mounting read-only | 096003817ad2638000a6836e55866697  SCRATCH_MNT/foo | mount: device write-protected, mounting read-only | 096003817ad2638000a6836e55866697  SCRATCH_MNT/foo`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; discard tests are sensitive to block-device discard support and whether allocated extents are accidentally punched on replacement devices. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
