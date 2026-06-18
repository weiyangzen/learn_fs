# sources/test-tools/xfstests/tests/generic/119

## Purpose

Reflinking two sets of files together: - Reflink identical parts of two identical files - Reflink identical parts of two other identical files - Reflink identical parts of all four files - Check that we end up with identical contents The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `119` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_arbitrary_fileset_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_test_reflink`
- Line 28: `_require_arbitrary_fileset_reflink`
- Line 37: `_pwrite_byte 0x61 0 $((blksz * 8)) $testdir/file1 >> $seqres.full`
- Line 38: `_pwrite_byte 0x62 0 $((blksz * 8)) $testdir/file2 >> $seqres.full`
- Line 39: `_pwrite_byte 0x63 0 $((blksz * 8)) $testdir/file3 >> $seqres.full`
- Line 40: `_pwrite_byte 0x64 0 $((blksz * 8)) $testdir/file4 >> $seqres.full`
- Line 59: `_reflink_range $testdir/file1 0 $testdir/file2 0 $((blksz * 4)) >> $seqres.full`
- Line 60: `_reflink_range $testdir/file3 0 $testdir/file4 0 $((blksz * 4)) >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 43: `md5sum $testdir/file1 | _filter_test_dir`
- Line 44: `md5sum $testdir/file2 | _filter_test_dir`
- Line 45: `md5sum $testdir/file3 | _filter_test_dir`
- Line 46: `md5sum $testdir/file4 | _filter_test_dir`
- Line 48: `_compare_range $testdir/file1 0 $testdir/file2 0 $((blksz * 8)) || echo "Files 1-2 do not match (intentional)"`
- Line 51: `_compare_range $testdir/file1 0 $testdir/file3 0 $((blksz * 8)) || echo "Files 1-3 do not match (intentional)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
