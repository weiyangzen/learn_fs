# sources/test-tools/xfstests/tests/btrfs/254

## Purpose
Test if the kernel can free the stale device entries. Override the default cleanup function. Use a known it is much easier to debug. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume raid`. Requirement and capability gates: line 32: `_require_scratch_dev_pool 3`; line 33: `_require_block_device $SCRATCH_DEV`; line 34: `_require_dm_target linear`; line 35: `_require_btrfs_forget_or_module_loadable`; line 36: `_require_scratch_nocheck`; line 37: `_require_command "$WIPEFS_PROG" wipefs`. Local helper surface: `cleanup_dmdev()` (line 15), `_cleanup()` (line 20), `setup_dmdev()` (line 45), `test_forget()` (line 65), `test_add_device()` (line 82). Important command/API calls include line 17: `_dmsetup_remove $node`; line 23: `rm -f $tmp.*`; line 24: `_unmount $seq_mnt > /dev/null 2>&1`; line 25: `rm -rf $seq_mnt > /dev/null 2>&1`; line 32: `_require_scratch_dev_pool 3`; line 33: `_require_block_device $SCRATCH_DEV`; line 34: `_require_dm_target linear`; line 35: `_require_btrfs_forget_or_module_loadable`; line 36: `_require_scratch_nocheck`; line 37: `_require_command "$WIPEFS_PROG" wipefs`; line 38: `_check_minimal_fs_size $((1024 * 1024 * 1024))`; line 40: `_fixed_by_kernel_commit 770c79fb6550 "btrfs: harden identification of a stale device"`; line 43: `_scratch_dev_pool_get 3`; line 55: `_dmsetup_create $node --table "$table" || _fail "setup dm device failed"`. It documents fixed kernel commit context at line 40: `_fixed_by_kernel_commit 770c79fb6550 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 254 | Label: none  uuid: <UUID> | 	Total devices <NUM> FS bytes used <SIZE> | 	devid <DEVID> size <SIZE> used <SIZE> path SCRATCH_DEV | 	*** Some devices missing`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
