# sources/test-tools/xfstests/tests/generic/130

## Purpose

xfs_io vector read/write and trunc tests. modified from cxfsqa tests - unixfile_basic_block_hole - unixfile_buffer_direct_coherency - unixfile_direct_rw - unixfile_eof_direct - unixfile_fsb_edge - unixfile_open_append - unixfile_open_trunc - unixfile_small_vector_async_rw - unixfile_small_vector_sync_rw The test is registered with `_begin_fstest pattern auto quick` and falls into the AIO/direct I/O, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `130` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_sparse_files`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 33: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x63 0 65536" -c "truncate 1" -c "pwrite -S 0x41 65536 65536" -c "pread -v 0 131072" $SCRATCH_MNT/eof-zeroing_direct | _filter_xfs_io_unique`
- Line 41: `$XFS_IO_PROG -f -t -c "truncate 8192" -c "pread -v 5000 3000" $SCRATCH_MNT/blackhole | _filter_xfs_io_unique`
- Line 47: `$XFS_IO_PROG -f -t -c "pwrite -S 0x41 8000 1000" -c "pwrite -S 0x57 4000 1000" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 51: `$XFS_IO_PROG -d -c "pwrite -S 0x78 20480 4096" -c "pwrite -S 0x79 4096 4096" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 55: `$XFS_IO_PROG -c "pread -v 0 9000" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 60: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x78 0 65536" -c "pread -v 0 65536" -c "pwrite -S 0x46 65536 6553600" -c "pread -v 0 6619136" $SCRATCH_MNT/direct_io | _filter_xfs_io_unique`
- Line 66: `$XFS_IO_PROG -d -c "pread -v 0 6619136" $SCRATCH_MNT/direct_io | _filter_xfs_io_unique`
- Line 69: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x61 0 65536" -c "pread -v 0 65536" -c "pwrite -S 0x62 65536 131072" -c "pread -v 0 131072" $SCRATCH_MNT/async_direct_io | _filter_xfs_io_unique`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 33: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x63 0 65536" -c "truncate 1" -c "pwrite -S 0x41 65536 65536" -c "pread -v 0 131072" $SCRATCH_MNT/eof-zeroing_direct | _filter_xfs_io_unique`
- Line 41: `$XFS_IO_PROG -f -t -c "truncate 8192" -c "pread -v 5000 3000" $SCRATCH_MNT/blackhole | _filter_xfs_io_unique`
- Line 47: `$XFS_IO_PROG -f -t -c "pwrite -S 0x41 8000 1000" -c "pwrite -S 0x57 4000 1000" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 51: `$XFS_IO_PROG -d -c "pwrite -S 0x78 20480 4096" -c "pwrite -S 0x79 4096 4096" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 55: `$XFS_IO_PROG -c "pread -v 0 9000" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 60: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x78 0 65536" -c "pread -v 0 65536" -c "pwrite -S 0x46 65536 6553600" -c "pread -v 0 6619136" $SCRATCH_MNT/direct_io | _filter_xfs_io_unique`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
