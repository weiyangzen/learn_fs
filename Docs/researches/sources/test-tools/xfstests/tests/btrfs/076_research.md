<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/076 -->
# sources/test-tools/xfstests/tests/btrfs/076

## Purpose
Regression test for btrfs incorrect inode ratio detection. The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, and its main coverage is: Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `compress` requirement gates: `_require_test`, `_require_scratch`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 10M" -c "fsync" \`; `$XFS_IO_PROG -f -c "pwrite 0 $((4096*33))" -c "fsync" \`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount "-o compress=lzo"`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite 0 10M" -c "fsync" \`; `$XFS_IO_PROG -f -c "pwrite 0 $((4096*33))" -c "fsync" \`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `if [[ $zone_append_max -gt 0 && $zone_append_max -lt $max_extent_size ]]; then`; `_scratch_mkfs >> $seqres.full 2>&1`; `$SCRATCH_MNT/data >> $seqres.full 2>&1`; plus 2 more source-matched operations.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/076 -->
