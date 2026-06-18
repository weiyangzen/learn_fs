# sources/test-tools/xfstests/tests/btrfs/286

## Purpose
Make sure btrfs dev-replace on missing device won't cause data corruption for NODATASUM data. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto replace raid`. Requirement and capability gates: line 15: `_require_command "$WIPEFS_PROG" wipefs`; line 17: `_require_fssum`; line 18: `_require_scratch_dev_pool 5`. Local helper surface: `workload()` (line 22). Important command/API calls include line 11: `_begin_fstest auto replace raid`; line 15: `_require_command "$WIPEFS_PROG" wipefs`; line 16: `_btrfs_get_profile_configs replace-missing`; line 17: `_require_fssum`; line 18: `_require_scratch_dev_pool 5`; line 19: `_scratch_dev_pool_get 4`; line 28: `rm -f $tmp.fssum`; line 29: `_scratch_pool_mkfs "$profile" >> $seqres.full 2>&1`; line 32: `_scratch_mount -o nodatasum`; line 35: `sync`; line 39: `$FSSUM_PROG -n -d -f -w $tmp.fssum $SCRATCH_MNT`; line 40: `_scratch_unmount`; line 46: `_scratch_mount -o degraded,nodatasum`; line 49: `echo "=== Verify the contents before replace ===" >> $seqres.full`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto replace raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 286 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
