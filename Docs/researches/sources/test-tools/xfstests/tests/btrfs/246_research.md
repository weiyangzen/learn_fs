# sources/test-tools/xfstests/tests/btrfs/246

## Purpose
Make sure btrfs can create compressed inline extents Override the default cleanup function. If it's subpage case, we don't support inline extents creation for now. This should create compressed inline extent success, all done. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick compress`. Requirement and capability gates: line 21: `_require_scratch`; line 24: `_require_btrfs_inline_extents_creation`. Local helper surface: `_cleanup()` (line 13). Important command/API calls include line 16: `rm -r -f $tmp.*`; line 21: `_require_scratch`; line 24: `_require_btrfs_inline_extents_creation`; line 26: `_scratch_mkfs > /dev/null`; line 27: `_scratch_mount -o compress,max_inline=2048`; line 30: `$XFS_IO_PROG -f -c "pwrite 0 2048" $SCRATCH_MNT/foobar > /dev/null`; line 31: `ino=$(stat -c %i $SCRATCH_MNT/foobar)`; line 32: `echo "sha256sum before mount cycle"`; line 33: `sha256sum $SCRATCH_MNT/foobar | _filter_scratch`; line 34: `_scratch_cycle_mount`; line 35: `echo "sha256sum after mount cycle"`; line 37: `_scratch_unmount`; line 39: `$BTRFS_UTIL_PROG inspect dump-tree -t 5 $SCRATCH_DEV | grep "($ino EXTENT_DATA 0" -A2 > $tmp.dump-tree`; line 42: `cat $tmp.dump-tree >> $seqres.full`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick compress`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 246 | sha256sum before mount cycle | 0ca3bfdeda1ef5036bfa5dad078a9f15724e79cf296bd4388cf786bfaf4195d0  SCRATCH_MNT/foobar | sha256sum after mount cycle | 0ca3bfdeda1ef5036bfa5dad078a9f15724e79cf296bd4388cf786bfaf4195d0  SCRATCH_MNT/foobar`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
