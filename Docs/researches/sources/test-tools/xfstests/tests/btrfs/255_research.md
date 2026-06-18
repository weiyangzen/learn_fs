# sources/test-tools/xfstests/tests/btrfs/255

## Purpose
Confirm that disabling quota during balance does not hang. The deadlock is fixed by kernel patch titled: btrfs: fix deadlock between quota disable and qgroup rescan worker Fill 40% of the device or 2GB Run btrfs balance and quota enable/disable in parallel. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior, multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto qgroup balance`. Requirement and capability gates: line 15: `_require_scratch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 13: `_begin_fstest auto qgroup balance`; line 15: `_require_scratch`; line 17: `_scratch_mkfs >> $seqres.full 2>&1`; line 18: `_scratch_mount`; line 24: `devsize=$(($(_get_device_size $SCRATCH_DEV) * 512))`; line 35: `_btrfs_stress_balance $SCRATCH_MNT >> $seqres.full &`; line 36: `balance_pid=$!`; line 37: `echo $balance_pid >> $seqres.full`; line 39: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; line 40: `$BTRFS_UTIL_PROG quota disable $SCRATCH_MNT`; line 43: `_btrfs_kill_stress_balance_pid $balance_pid`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto qgroup balance`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, enables and inspects quota groups. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 255 | Silence is golden`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits; device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
