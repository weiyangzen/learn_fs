# sources/test-tools/xfstests/tests/generic/200

## Purpose

Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone punch prealloc` and falls into the reflink/CoW, AIO/direct I/O, preallocation/unwritten extent, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `200` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_cp_reflink`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 32: `_require_scratch_reflink`
- Line 34: `_require_xfs_io_command "falloc"`
- Line 35: `_require_xfs_io_command "fpunch"`
- Line 36: `_require_cp_reflink`
- Line 51: `_weave_reflink_rainbow $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 62: `_weave_reflink_rainbow_delalloc $blksz $nr $testdir/file3 >> $seqres.full`
- Line 64: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 65: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 55: `md5sum $testdir/file1 | _filter_scratch`
- Line 56: `md5sum $testdir/file3 | _filter_scratch`
- Line 57: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
