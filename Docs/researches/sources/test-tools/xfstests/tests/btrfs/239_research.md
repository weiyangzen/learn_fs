# sources/test-tools/xfstests/tests/btrfs/239

## Purpose
FSQA Test No. 239 Test a particular scenario where we fsync a directory, then move one of its children directories into another directory and then finally sync the log trees by fsyncing any other inode. We want to check that after a power failure we are able to mount the filesystem and that the moved directory exists only as a child of the directory we moved it into. Override the default cleanup function. The test requires a very specific layout of keys and items in the fs/subvolume btree to trigger a bug. So we want to make sure that on whatever platform we. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick log`. Requirement and capability gates: line 27: `_require_scratch`; line 28: `_require_dm_target flakey`; line 39: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 21: `rm -f $tmp.*`; line 27: `_require_scratch`; line 28: `_require_dm_target flakey`; line 38: `_scratch_mkfs "-n 65536" >>$seqres.full 2>&1`; line 39: `_require_metadata_journaling $SCRATCH_DEV`; line 41: `_scratch_mount`; line 44: `mkdir $SCRATCH_MNT/testdir`; line 81: `mkdir $SCRATCH_MNT/testdir/dira`; line 93: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT`; line 96: `sync`; line 141: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir`; line 150: `mv $SCRATCH_MNT/testdir/dira $SCRATCH_MNT/`; line 156: `$XFS_IO_PROG -c "pwrite -S 0xab 0 64K" -c "fsync" $SCRATCH_MNT/testdir/file1 >>$seqres.full`; line 188: `_flakey_drop_and_remount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick log`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 239 | File SCRATCH_MNT/testdir/file1 data: | 0000000 ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab | * | 0065536`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
