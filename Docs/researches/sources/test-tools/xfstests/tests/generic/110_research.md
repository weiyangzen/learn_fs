# sources/test-tools/xfstests/tests/generic/110

## Purpose

Tests file clone functionality of btrfs ("reflinks"): - Reflink a file - Reflink the reflinked file - Modify the original file - Modify the reflinked file The test is registered with `_begin_fstest auto quick clone fiemap` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `110` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. common/filter`, `. common/reflink` and gates execution with `_require_test_reflink`, `_require_xfs_io_command "fiemap"`, `_require_cp_reflink`, `_require_test`. Local helpers are `line 37 `_checksum_files() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_test_reflink`
- Line 30: `_require_cp_reflink`
- Line 45: `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 9000' $testdir1/original >> $seqres.full 2>&1`
- Line 47: `cp --reflink $testdir1/original $testdir1/copy1`
- Line 48: `cp --reflink $testdir1/copy1 $testdir1/copy2`
- Line 49: `_verify_reflink $testdir1/original $testdir1/copy1`
- Line 50: `_verify_reflink $testdir1/original $testdir1/copy2`
- Line 55: `$XFS_IO_PROG -c 'pwrite -S 0x62 0 9000' $testdir1/original >> $seqres.full 2>&1`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 40: `md5sum $testdir1/$F | _filter_test_dir`
- Line 49: `_verify_reflink $testdir1/original $testdir1/copy1`
- Line 50: `_verify_reflink $testdir1/original $testdir1/copy2`
- Line 51: `echo "Original md5sums:"`
- Line 57: `echo "md5sums after overwriting original:"`
- Line 63: `echo "md5sums after overwriting copy1:"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
