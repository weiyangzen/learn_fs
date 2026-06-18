# sources/test-tools/xfstests/tests/generic/171

## Purpose

Reflink a file, use up the rest of the space, then try to observe ENOSPC while copy-on-writing the file via the page cache. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, xattr, ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `171` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 50: `_pwrite_byte 0x61 0 $((blksz * nr_blks)) $testdir/bigfile >> $seqres.full 2>&1`
- Line 51: `_cp_reflink $testdir/bigfile $testdir/clonefile`
- Line 60: `out="$(_pwrite_byte 0x62 0 $((blksz * nr_blks)) $testdir/bigfile 2>&1 | _filter_xfs_io_error)"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 55: `nr_free=$(stat -f -c '%f' $testdir)`
- Line 60: `out="$(_pwrite_byte 0x62 0 $((blksz * nr_blks)) $testdir/bigfile 2>&1 | _filter_xfs_io_error)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
