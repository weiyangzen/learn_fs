<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/116 -->
# sources/test-tools/xfstests/tests/btrfs/116

## Purpose
Verify that when a fitrim operation is made against a btrfs filesystem, the ranges [0, 64Kb[ and [68Kb, 1Mb[ of the device are not discarded, they remain with the content they had before the fitrim operation. These regions of the device are reserved for a boot loader to use at its will. The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, and its main coverage is: Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `metadata` requirement gates: `_require_scratch`, `_require_non_zoned_device`, `_require_batched_discard`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -c "pwrite -S 0xfd 0 64K" $SCRATCH_DEV | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xfd 68K 956K" $SCRATCH_DEV | _filter_xfs_io`; `$FSTRIM_PROG $SCRATCH_MNT`; `od -t x1 -N $((64 * 1024)) $SCRATCH_DEV`; `od -t x1 -j $((68 * 1024)) -N $((956 * 1024)) $SCRATCH_DEV` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -c "pwrite -S 0xfd 0 64K" $SCRATCH_DEV | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xfd 68K 956K" $SCRATCH_DEV | _filter_xfs_io`; `$FSTRIM_PROG $SCRATCH_MNT`; `od -t x1 -N $((64 * 1024)) $SCRATCH_DEV`; `od -t x1 -j $((68 * 1024)) -N $((956 * 1024)) $SCRATCH_DEV`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Verifies discard persistence at raw device offsets. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, non-zoned device semantics, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/116 -->
