<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/090 -->
# sources/test-tools/xfstests/tests/btrfs/090

## Purpose
Check return value of "btrfs filesystem show" command executed on umounted device. It should return 0 if nothing wrong happens. btrfs-progs: Fix wrong return value when executing 'fi show' on umounted device. The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, and its main coverage is: Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `metadata` requirement gates: `_require_scratch`, `_require_scratch_dev_pool`. The important external command surfaces are `_btrfs filesystem show $FIRST_POOL_DEV | \` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"`. The core workload then performs these representative operations: `_btrfs filesystem show $FIRST_POOL_DEV | \`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, multi-device scratch pool, btrfs-progs command wrappers, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/090 -->
