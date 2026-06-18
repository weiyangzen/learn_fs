# sources/test-tools/xfstests/tests/btrfs/296

## Purpose
Make sure that per-fs features sysfs interface get properly updated when a new feature is added. We need the global features support Make sure we have support RAID1C34 first Go the very basic profile first, so that even older progs can support it. First we need per-fs features directory Make sure the per-fs features doesn't include raid1c34 Balance to RAID1C3 Sync before checking for sysfs update during cleaner_kthread(). In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick balance raid`. Requirement and capability gates: line 13: `_require_scratch_dev_pool 3`; line 18: `_require_btrfs_fs_sysfs`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 11: `_begin_fstest auto quick balance raid`; line 13: `_require_scratch_dev_pool 3`; line 14: `_fixed_by_kernel_commit b7625f461da6 "btrfs: sysfs: update fs features directory asynchronously"`; line 18: `_require_btrfs_fs_sysfs`; line 26: `_scratch_dev_pool_get 3`; line 29: `_scratch_pool_mkfs -m dup -d single >> $seqres.full 2>&1`; line 31: `_scratch_mount`; line 46: `$BTRFS_UTIL_PROG balance start -mconvert=raid1c3 "$SCRATCH_MNT" >> $seqres.full`; line 49: `sync`; line 59: `_scratch_unmount`; line 60: `_scratch_dev_pool_put`. It documents fixed kernel commit context at line 14: `_fixed_by_kernel_commit b7625f461da6 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick balance raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 296 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
