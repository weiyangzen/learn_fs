<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/115 -->
# sources/test-tools/xfstests/tests/btrfs/115

## Purpose
btrfs quota scan/disable sanity test Make sure that disabling quotas during a quota rescan doesn't crash The script is categorized by `_begin_fstest` as `auto`, `qgroup`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent.

## Important APIs, Types, and Functions
fstest tags: `auto`, `qgroup` requirement gates: `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG quota disable $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG quota disable $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; `for i in `seq 0 1 450000`; do`.

## State and Persistence Behavior
Mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/115 -->
