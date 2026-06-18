# sources/test-tools/xfstests/tests/generic/142

## Purpose

Ensure that reflinking a file N times and CoWing the copies leaves the original intact. - Create a file and record its hash - Create some reflink copies - Rewrite all the reflink copies - Compare the contents of the original file The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `142` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_test_reflink`
- Line 29: `_require_cp_reflink`
- Line 39: `_pwrite_byte 0x61 0 $((blksz * 256)) $testdir/file1 >> $seqres.full`
- Line 47: `_cp_reflink $testdir/file1 $testdir/file$i`
- Line 53: `_pwrite_byte 0x62 0 $((blksz * 256)) $testdir/file$i >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 42: `md5sum $testdir/file1 | _filter_test_dir`
- Line 59: `md5sum $testdir/file2 | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
