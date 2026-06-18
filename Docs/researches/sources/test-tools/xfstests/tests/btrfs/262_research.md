# sources/test-tools/xfstests/tests/btrfs/262

## Purpose
Test that running qgroup enable, create, destroy, and disable commands in parallel doesn't result in a deadlock, a crash or any filesystem inconsistency. success, all done. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick qgroup`. Requirement and capability gates: line 17: `_require_scratch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 12: `_begin_fstest auto quick qgroup`; line 17: `_require_scratch`; line 19: `_scratch_mkfs > /dev/null 2>&1`; line 20: `_scratch_mount`; line 23: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT 2>> $seqres.full &`; line 24: `$BTRFS_UTIL_PROG qgroup create 1/0 $SCRATCH_MNT 2>> $seqres.full &`; line 25: `$BTRFS_UTIL_PROG qgroup destroy 1/0 $SCRATCH_MNT 2>> $seqres.full &`; line 26: `$BTRFS_UTIL_PROG quota disable $SCRATCH_MNT 2>> $seqres.full &`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick qgroup`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, enables and inspects quota groups. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 262 | Silence is golden`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
