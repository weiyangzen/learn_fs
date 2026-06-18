# sources/test-tools/xfstests/tests/generic/111

## Purpose

Tests file clone functionality of btrfs ("reflinks") on directory trees. - Create directory and subdirectory, each having one file - Create 2 recursive reflinked copies of the tree - Modify the original files - Modify one of the copies The test is registered with `_begin_fstest auto quick clone fiemap` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `111` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. common/filter`, `. common/reflink` and gates execution with `_require_test_reflink`, `_require_xfs_io_command "fiemap"`, `_require_cp_reflink`, `_require_test`. Local helpers are `line 38 `_checksum_files() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_test_reflink`
- Line 31: `_require_cp_reflink`
- Line 51: `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 9000' $testdir1/original/file1 >> $seqres.full 2>&1`
- Line 53: `$XFS_IO_PROG -f -c 'pwrite -S 0x62 0 11000' $testdir1/original/subdir/file2 >> $seqres.full 2>&1`
- Line 55: `cp --recursive --reflink $testdir1/original $testdir1/copy1`
- Line 56: `cp --recursive --reflink $testdir1/copy1 $testdir1/copy2`
- Line 58: `_verify_reflink $testdir1/original/file1 $testdir1/copy1/file1`
- Line 59: `_verify_reflink $testdir1/original/subdir/file2 $testdir1/copy1/subdir/file2`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 43: `md5sum $testdir1/$F | _filter_test_dir`
- Line 58: `_verify_reflink $testdir1/original/file1 $testdir1/copy1/file1`
- Line 59: `_verify_reflink $testdir1/original/subdir/file2 $testdir1/copy1/subdir/file2`
- Line 61: `_verify_reflink $testdir1/original/file1 $testdir1/copy2/file1`
- Line 62: `_verify_reflink $testdir1/original/subdir/file2 $testdir1/copy2/subdir/file2`
- Line 65: `echo "Original md5sums:"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
