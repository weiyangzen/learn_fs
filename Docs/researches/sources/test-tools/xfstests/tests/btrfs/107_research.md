<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/107 -->
# sources/test-tools/xfstests/tests/btrfs/107

## Purpose
Test that calling fallocate against a range which is already allocated does not truncate beyond EOF The script is categorized by `_begin_fstest` as `auto`, `quick`, `prealloc`, and its main coverage is: Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `prealloc` requirement gates: `_require_scratch`, `_require_xfs_io_command`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 $filesize" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "falloc 0 $fallocrange" $SCRATCH_MNT/foo` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite 0 $filesize" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "falloc 0 $fallocrange" $SCRATCH_MNT/foo`. It also uses background or repeated stress/control loops: `_scratch_mkfs > /dev/null 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io subcommand availability, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/107 -->
