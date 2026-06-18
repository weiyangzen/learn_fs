# sources/test-tools/xfstests/tests/generic/104

## Purpose

fsync only one of the files, after the fsync log/journal is replayed all the links exist and the filesystem metadata (directory and file inodes) is in a consistent state. The test is registered with `_begin_fstest auto quick metadata log` and falls into the journal/power-failure replay, hard link area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `104` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey` and gates execution with `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 45: `ln $SCRATCH_MNT/testdir/bar $SCRATCH_MNT/testdir/bar_link`
- Line 46: `ln $SCRATCH_MNT/testdir/foo $SCRATCH_MNT/testdir/foo_link`
- Line 47: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir/bar`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 52: `echo "Link count for file foo: $(stat -c %h $SCRATCH_MNT/testdir/foo)"`
- Line 53: `echo "Link count for file bar: $(stat -c %h $SCRATCH_MNT/testdir/bar)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `_cleanup_flakey`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The simulated crash path depends on dm-flakey teardown/remount ordering; a cleanup or remount failure can mask the metadata replay condition being tested. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
