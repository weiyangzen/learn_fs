# sources/test-tools/xfstests/tests/generic/112

## Purpose

check if preallocation is supported, xfs_io resvsp command only prints out messages on failure. The test is registered with `_begin_fstest rw aio auto quick` and falls into the AIO/direct I/O, preallocation/unwritten extent, timestamp, rename, fsx random I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `112` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_aio`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 18: `rm -rf $TEST_DIR/fsx.* $tmp.*`
- Line 56: `if ! $FSX_PROG $_param -P "$RESULT_DIR" $FSX_AVOID $seq.$_n &>/dev/null`
- Line 59: `mv "$RESULT_DIR"/$seq.$_n.fsxlog $seqres.$_n.full`
- Line 103: `[ -x $here/ltp/aio-stress ] || _notrun "fsx not built with AIO for this platform"`
- Line 124: `testio=`$XFS_IO_PROG -f -c "resvsp 0 1" $testfile 2>&1``
- Line 142: `rm -f $seq.*.fsx{good,log}`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Timestamp resolution and mount options can make the signal weak unless the test accounts for atime/mtime/ctime granularity. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0	# success is the default!; status=1; exit; status=1; exit; exit; exit 0`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
