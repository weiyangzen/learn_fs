# sources/test-tools/xfstests/tests/generic/132

## Purpose

xfs_io aligned vector rw created from CXFSQA test unixfile_vector_aligned_rw The test is registered with `_begin_fstest pattern auto` and falls into the generic filesystem behavior area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `132` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 22: `$XFS_IO_PROG -f -t -c "pwrite -S 0x63 0 512" -c "pwrite -S 0x64 512 512" -c "pwrite -S 0x65 1024 512" -c "pwrite -S 0x66 1536 512" -c "pwrite -S 0x67 2048 512" -c "pwrite -S 0x68 2560 512" -c "pwrite -S 0x69 3072 512" -c`
- Line 40: `$XFS_IO_PROG -f -c "pwrite -S 0x63 4096 1024" -c "pwrite -S 0x6B 5120 1024" -c "pwrite -S 0x6C 6144 1024" -c "pwrite -S 0x6D 7168 1024" -c "pread -v 0 1024" -c "pread -v 1024 1024" -c "pread -v 2048 1024" -c "pread -v 30`
- Line 54: `$XFS_IO_PROG -f -c "pwrite -S 0x6E 8192 2048" -c "pwrite -S 0x6F 10240 2048" -c "pread -v 0 2048" -c "pread -v 2048 2048" -c "pread -v 4096 2048" -c "pread -v 6144 2048" -c "pread -v 8192 2048" -c "pread -v 10240 2048" $`
- Line 64: `$XFS_IO_PROG -f -c "pwrite -S 0x70 12288 4096" -c "pread -v 0 4096" -c "pread -v 4096 4096" -c "pread -v 8192 4096" -c "pread -v 12288 4096" $SCRATCH_MNT/aligned_vector_rw | _filter_xfs_io_unique`
- Line 71: `$XFS_IO_PROG -f -c "pwrite -S 0x71 16384 8192" -c "pwrite -S 0x72 24576 8192" -c "pread -v 0 8192" -c "pread -v 8192 8192" -c "pread -v 8192 8192" -c "pread -v 16384 8192" $SCRATCH_MNT/aligned_vector_rw | _filter_xfs_io_`
- Line 79: `$XFS_IO_PROG -f -c "pwrite -S 0x73 32768 16384" -c "pwrite -S 0x74 49152 16384" -c "pread -v 0 16384" -c "pread -v 16384 16384" -c "pread -v 32768 16384" -c "pread -v 49152 16384" $SCRATCH_MNT/aligned_vector_rw | _filter`
- Line 87: `$XFS_IO_PROG -f -c "pwrite -S 0x75 65536 32768" -c "pwrite -S 0x76 98304 32768" -c "pread -v 0 32768" -c "pread -v 32768 32768" -c "pread -v 65536 32768" -c "pread -v 98304 32768" $SCRATCH_MNT/aligned_vector_rw | _filter`
- Line 95: `$XFS_IO_PROG -f -c "pwrite -S 0x76 131072 65536" -c "pwrite -S 0x77 196608 65536" -c "pread -v 0 65536" -c "pread -v 65536 65536" -c "pread -v 131072 65536" -c "pread -v 196608 65536" $SCRATCH_MNT/aligned_vector_rw | _fi`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 22: `$XFS_IO_PROG -f -t -c "pwrite -S 0x63 0 512" -c "pwrite -S 0x64 512 512" -c "pwrite -S 0x65 1024 512" -c "pwrite -S 0x66 1536 512" -c "pwrite -S 0x67 2048 512" -c "pwrite -S 0x68 2560 512" -c "pwrite -S 0x69 3072 512" -c`
- Line 40: `$XFS_IO_PROG -f -c "pwrite -S 0x63 4096 1024" -c "pwrite -S 0x6B 5120 1024" -c "pwrite -S 0x6C 6144 1024" -c "pwrite -S 0x6D 7168 1024" -c "pread -v 0 1024" -c "pread -v 1024 1024" -c "pread -v 2048 1024" -c "pread -v 30`
- Line 54: `$XFS_IO_PROG -f -c "pwrite -S 0x6E 8192 2048" -c "pwrite -S 0x6F 10240 2048" -c "pread -v 0 2048" -c "pread -v 2048 2048" -c "pread -v 4096 2048" -c "pread -v 6144 2048" -c "pread -v 8192 2048" -c "pread -v 10240 2048" $`
- Line 64: `$XFS_IO_PROG -f -c "pwrite -S 0x70 12288 4096" -c "pread -v 0 4096" -c "pread -v 4096 4096" -c "pread -v 8192 4096" -c "pread -v 12288 4096" $SCRATCH_MNT/aligned_vector_rw | _filter_xfs_io_unique`
- Line 71: `$XFS_IO_PROG -f -c "pwrite -S 0x71 16384 8192" -c "pwrite -S 0x72 24576 8192" -c "pread -v 0 8192" -c "pread -v 8192 8192" -c "pread -v 8192 8192" -c "pread -v 16384 8192" $SCRATCH_MNT/aligned_vector_rw | _filter_xfs_io_`
- Line 79: `$XFS_IO_PROG -f -c "pwrite -S 0x73 32768 16384" -c "pwrite -S 0x74 49152 16384" -c "pread -v 0 16384" -c "pread -v 16384 16384" -c "pread -v 32768 16384" -c "pread -v 49152 16384" $SCRATCH_MNT/aligned_vector_rw | _filter`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
