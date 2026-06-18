# sources/test-tools/xfstests/tests/btrfs/242

## Purpose
Test that fstrim can run on the degraded filesystem Kernel requires fix for the null pointer deref in btrfs_trim_fs() [patch] btrfs: check for missing device in btrfs_trim_fs Add a test file with some data. Unmount the filesystem. Mount the filesystem in degraded mode Run fstrim, it should skip on the missing device. Verify data integrity as in the golden output. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, discard/trim behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume trim raid`. Requirement and capability gates: line 16: `_require_btrfs_forget_or_module_loadable`; line 17: `_require_scratch_dev_pool 2`; line 24: `_require_batched_discard $SCRATCH_MNT`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_require_btrfs_forget_or_module_loadable`; line 17: `_require_scratch_dev_pool 2`; line 19: `_scratch_dev_pool_get 2`; line 22: `_scratch_pool_mkfs "-m raid1 -d raid1"`; line 23: `_scratch_mount`; line 24: `_require_batched_discard $SCRATCH_MNT`; line 27: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 10M" $SCRATCH_MNT/foo | _filter_xfs_io`; line 30: `_scratch_unmount`; line 33: `_btrfs_forget_or_module_reload`; line 34: `_mount -o degraded $dev1 $SCRATCH_MNT`; line 43: `_scratch_dev_pool_put`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume trim raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 242 | wrote 10485760/10485760 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | File foo data: | 0000000 ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab | * | 10485760`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; discard tests are sensitive to block-device discard support and whether allocated extents are accidentally punched on replacement devices. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
