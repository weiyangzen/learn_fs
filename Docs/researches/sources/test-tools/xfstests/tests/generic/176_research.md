# sources/test-tools/xfstests/tests/generic/176

## Purpose

Setup for one million blocks, but we'll accept stress testing down to 2^17 blocks... that should be plenty for anyone. The test is registered with `_begin_fstest auto clone punch` and falls into the reflink/CoW, xattr, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `176` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`. Local helpers are `line 37 `calc_space() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 17: `_require_scratch_reflink`
- Line 18: `_require_cp_reflink`
- Line 19: `_require_xfs_io_command "fpunch"`
- Line 50: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b 4194304 0 $((2 ** (fnr + 1) * blksz))" "$testdir/file1" >> "$seqres.full"`
- Line 59: `_reflink_range "$testdir/file1" 0 "$testdir/file2" 0 $bytes >> "$seqres.full"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 34: `free_blocks=$(stat -f -c '%a' "$testdir")`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
