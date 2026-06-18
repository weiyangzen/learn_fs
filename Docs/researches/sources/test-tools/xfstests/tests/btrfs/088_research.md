<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/088 -->
# sources/test-tools/xfstests/tests/btrfs/088

## Purpose
Test that btrfs' transaction abortion does not corrupt a filesystem mounted with -o discard nor allows a subsequent fstrim to corrupt the filesystem This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, and its main coverage is: Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
local shell functions: `enable_io_failure`, `disable_io_failure` fstest tags: `auto`, `quick`, `metadata` requirement gates: `_require_scratch`, `_require_fail_make_request`, `_require_batched_discard`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xbb 512K 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$FSTRIM_PROG $SCRATCH_MNT`; `od -t x1 $SCRATCH_MNT/foo` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o discard"`; `_scratch_cycle_mount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xbb 512K 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$FSTRIM_PROG $SCRATCH_MNT`; `od -t x1 $SCRATCH_MNT/foo`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; `touch $SCRATCH_MNT/abc >>$seqres.full 2>&1 && \`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; verifies discard persistence at raw device offsets. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/088 -->
