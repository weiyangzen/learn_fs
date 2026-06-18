# sources/test-tools/xfstests/tests/generic/214

## Purpose

We don't remove files after they are written to check for subsequent fs corruption at the end The test is registered with `_begin_fstest rw auto prealloc quick` and falls into the AIO/direct I/O, preallocation/unwritten extent, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `214` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_xfs_io_command "falloc"`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `[ -n "$XFS_IO_PROG" ] || _notrun "xfs_io executable not found"`
- Line 33: `_require_xfs_io_command "falloc"`
- Line 43: `echo "=== falloc & read  ==="`
- Line 44: `$XFS_IO_PROG -f -c 'falloc 0 4096' -c 'pread -v 0 4096' $TEST_DIR/test214-1 | _filter_xfs_io_unique`
- Line 52: `echo "=== falloc, write beginning, read ==="`
- Line 53: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 0 1' -c 'pread -v 0 512' $TEST_DIR/test214-2 | _filter_xfs_io_unique`
- Line 60: `echo "=== falloc, write middle, read ==="`
- Line 61: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 256 1' -c 'pread -v 0 512' $TEST_DIR/test214-3 | _filter_xfs_io_unique`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 44: `$XFS_IO_PROG -f -c 'falloc 0 4096' -c 'pread -v 0 4096' $TEST_DIR/test214-1 | _filter_xfs_io_unique`
- Line 53: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 0 1' -c 'pread -v 0 512' $TEST_DIR/test214-2 | _filter_xfs_io_unique`
- Line 61: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 256 1' -c 'pread -v 0 512' $TEST_DIR/test214-3 | _filter_xfs_io_unique`
- Line 69: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 511 1' -c 'pread -v 0 512' $TEST_DIR/test214-4 | _filter_xfs_io_unique`
- Line 87: `$XFS_IO_PROG -f -c 'falloc         0x0     0x65C00' -c 'pwrite -S 0xAA 0x12000 0x10000' -c 'fsync' -c 'truncate 0x16000' $TEST_DIR/test214-5 | _filter_xfs_io_unique`
- Line 95: `$XFS_IO_PROG -f -d -c 'pread -v 0 0x16000' $TEST_DIR/test214-5 | _filter_xfs_io_unique`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
