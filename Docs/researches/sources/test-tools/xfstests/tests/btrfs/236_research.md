# sources/test-tools/xfstests/tests/btrfs/236

## Purpose
FSQA Test No. 236 Test for fsync data loss after renaming a file or adding a hard link, with a previous fsync of another file, as well as that mtime and ctime are correct. Test both with COW and NOCOW writes. Override the default cleanup function. The comments inside the function mentioning specific inode numbers and IDs (transactions, log commits, etc) are for the case where the function is run on a freshly created filesystem, but the logic and reasoning still applies for future invocations. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick log`. Requirement and capability gates: line 25: `_require_scratch`; line 26: `_require_dm_target flakey`; line 157: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 15), `test_fsync()` (line 32). Important command/API calls include line 19: `rm -f $tmp.*`; line 25: `_require_scratch`; line 26: `_require_dm_target flakey`; line 32: `test_fsync()`; line 52: `touch $bar`; line 68: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1M" -c "fsync" $baz >>$seqres.full`; line 85: `mv $baz $foo`; line 87: `ln $baz $foo`; line 98: `$XFS_IO_PROG -c "pwrite -S 0xcd 0 1M" $foo >>$seqres.full`; line 103: `$XFS_IO_PROG -c "fsync" $bar`; line 124: `$XFS_IO_PROG -c "fsync" $foo`; line 131: `digest_before=$(_md5_checksum $foo)`; line 132: `mtime_before=$(stat -c %Y $foo)`; line 133: `ctime_before=$(stat -c %Z $foo)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick log`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 236 | Testing fsync after rename with COW writes | Testing fsync after link with COW writes | Testing fsync after rename with NOCOW writes | Testing fsync after link with NOCOW writes`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
