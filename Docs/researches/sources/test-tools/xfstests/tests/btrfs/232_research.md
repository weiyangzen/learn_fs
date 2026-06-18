# sources/test-tools/xfstests/tests/btrfs/232

## Purpose
Test that performing io and exhausting qgroup limit won't deadlock. This exercises issues fixed by the following kernel commits: 4f6a49de64fd ("btrfs: unlock extents in btrfs_zero_range in case of quota reservation errors") 4d14c5cde5c2 ("btrfs: don't flush from btrfs_delayed_inode_reserve_metadata") This test requires specific data space usage, skip if we have compression enabled. Make sure the data reach disk so later qgroup scan can see it set the limit to 1 g, leaving us just 100mb of slack space. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick qgroup limit`. Requirement and capability gates: line 34: `_require_no_compress`; line 36: `_require_scratch_size $((2 * 1024 * 1024))`. Local helper surface: `writer()` (line 19). Important command/API calls include line 15: `_begin_fstest auto quick qgroup limit`; line 34: `_require_no_compress`; line 36: `_require_scratch_size $((2 * 1024 * 1024))`; line 37: `_scratch_mkfs > /dev/null 2>&1`; line 38: `_scratch_mount`; line 42: `sync`; line 44: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; line 45: `_qgroup_rescan $SCRATCH_MNT >> $seqres.full`; line 47: `$BTRFS_UTIL_PROG qgroup limit 1G 0/5 $SCRATCH_MNT`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick qgroup limit`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, enables and inspects quota groups. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 232 | Silence is golden`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
