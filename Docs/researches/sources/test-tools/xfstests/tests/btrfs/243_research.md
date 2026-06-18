# sources/test-tools/xfstests/tests/btrfs/243

## Purpose
Test that if we explicitly fsync a file that was previously renamed and its size was increased through a truncate operation, after a power failure the file has the size set by truncate operation. In between the truncation and the fsync, there was a rename of another file in the same directory and that file was also fsynced before we fsynced the file that was truncated. Create our test files. Make them durably persisted. Fsync bar, this will be a noop since the file has not yet been modified in the current transaction. The goal here is to clear BTRFS_INODE_NEEDS_FULL_SYNC. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick log`. Requirement and capability gates: line 26: `_require_scratch`; line 27: `_require_dm_target flakey`; line 32: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 16). Important command/API calls include line 20: `rm -r -f $tmp.*`; line 26: `_require_scratch`; line 27: `_require_dm_target flakey`; line 29: `rm -f $seqres.full`; line 31: `_scratch_mkfs >>$seqres.full 2>&1`; line 32: `_require_metadata_journaling $SCRATCH_DEV`; line 34: `_scratch_mount`; line 37: `touch $SCRATCH_MNT/foo`; line 38: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/bar | _filter_xfs_io`; line 41: `sync`; line 46: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`; line 49: `mv $SCRATCH_MNT/bar $SCRATCH_MNT/bar2`; line 50: `mv $SCRATCH_MNT/foo $SCRATCH_MNT/foo2`; line 53: `$XFS_IO_PROG -c "truncate 2M" $SCRATCH_MNT/bar2`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick log`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 243 | wrote 1048576/1048576 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | File bar2 content before power failure: | 0000000 ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab | * | 1048576 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | * | ... (15 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
