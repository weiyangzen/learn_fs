# sources/test-tools/xfstests/tests/generic/215

## Purpose

Based on the testcase in http://bugzilla.kernel.org/show_bug.cgi?id=2645 The test is registered with `_begin_fstest auto metadata quick mmap` and falls into the mmap, timestamp area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `215` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 12: `_begin_fstest auto metadata quick mmap`
- Line 26: `testfile=$TEST_DIR/tst.mmap`
- Line 30: `dd if=/dev/zero of=$testfile count=4096`
- Line 38: `echo "writing via mmap"`
- Line 39: `$XFS_IO_PROG -f -c 'mmap 0 4096' -c 'mwrite 0 4096' $testfile | _filter_xfs_io_unique`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 32: `mtime1=`stat -c "%Y" $testfile``
- Line 33: `ctime1=`stat -c "%Z" $testfile``
- Line 39: `$XFS_IO_PROG -f -c 'mmap 0 4096' -c 'mwrite 0 4096' $testfile | _filter_xfs_io_unique`
- Line 44: `mtime2=`stat -c "%Y" $testfile``
- Line 45: `ctime2=`stat -c "%Z" $testfile``

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Timestamp resolution and mount options can make the signal weak unless the test accounts for atime/mtime/ctime granularity. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
