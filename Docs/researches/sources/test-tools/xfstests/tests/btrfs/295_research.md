# sources/test-tools/xfstests/tests/btrfs/295

## Purpose
Make sure btrfs handles critical errors gracefully during mount. Directly writing to the device, which may not work with a zoned device Use single metadata profile so we only need to corrupt one copy of tree block mount may lead to crash Re-create the fs to avoid false alert from the corrupted fs. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick dangerous`. Requirement and capability gates: line 13: `_require_scratch`; line 15: `_require_non_zoned_device "$SCRATCH_DEV"`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 13: `_require_scratch`; line 15: `_require_non_zoned_device "$SCRATCH_DEV"`; line 18: `_scratch_mkfs -m single > $seqres.full`; line 20: `logical_root=$($BTRFS_UTIL_PROG inspect dump-tree -t root "$SCRATCH_DEV" | grep leaf | head -n1 | cut -f2 -d\ )`; line 22: `physical_root=$(_btrfs_get_physical $logical_root 1)`; line 30: `_try_scratch_mount >> $seqres.full 2>&1`; line 35: `_scratch_mkfs -m single >> $seqres.full`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick dangerous`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 295 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
