# sources/test-tools/xfstests/tests/generic/177

## Purpose

Create out test file with some data and then fsync it. We do the fsync only to make sure the last fsync we do in this test triggers the fast code path of btrfs' fsync implementation, a condition necessary to trigger the bug btrfs had. The test is registered with `_begin_fstest auto quick prealloc metadata punch log fiemap` and falls into the journal/power-failure replay, preallocation/unwritten extent, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `177` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`, `. ./common/dmflakey` and gates execution with `_require_scratch`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 30: `_require_xfs_io_command "fpunch"`
- Line 45: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K $(($BLOCK_SIZE * 32))" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io_blocks_modified`
- Line 50: `$XFS_IO_PROG -c "fpunch $(($BLOCK_SIZE * 24)) $(($BLOCK_SIZE * 8))" $SCRATCH_MNT/foobar`
- Line 54: `$XFS_IO_PROG -c "fpunch $(($BLOCK_SIZE * 16)) $(($BLOCK_SIZE * 32))" $SCRATCH_MNT/foobar`
- Line 58: `$XFS_IO_PROG -c "fpunch $(($BLOCK_SIZE * 8)) $(($BLOCK_SIZE * 24))" $SCRATCH_MNT/foobar`
- Line 62: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foobar`
- Line 68: `$XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar | _filter_fiemap $BLOCK_SIZE`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 45: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K $(($BLOCK_SIZE * 32))" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io_blocks_modified`
- Line 68: `$XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar | _filter_fiemap $BLOCK_SIZE`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `_cleanup_flakey`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The simulated crash path depends on dm-flakey teardown/remount ordering; a cleanup or remount failure can mask the metadata replay condition being tested. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
