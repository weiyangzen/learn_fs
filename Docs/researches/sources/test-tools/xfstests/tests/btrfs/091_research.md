<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/091 -->
# sources/test-tools/xfstests/tests/btrfs/091

## Purpose
Test for incorrect exclusive reference count after cloning file between subvolumes. The script is categorized by `_begin_fstest` as `auto`, `quick`, `qgroup`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `qgroup` requirement gates: `_require_scratch`, `_require_cp_reflink`, `_require_scratch_qgroup`. The important external command surfaces are `_btrfs subvolume create $SCRATCH_MNT/subv1`; `_btrfs subvolume create $SCRATCH_MNT/subv2`; `_btrfs subvolume create $SCRATCH_MNT/subv3`; `_btrfs quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | $SED_PROG -n '/[0-9]/p' | \` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 256K" $SCRATCH_MNT/subv1/file1 | _filter_xfs_io`; `cp --reflink $SCRATCH_MNT/subv1/file1 $SCRATCH_MNT/subv2/file1`; `cp --reflink $SCRATCH_MNT/subv1/file1 $SCRATCH_MNT/subv3/file1` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `run_check _scratch_mkfs "--nodesize $NODESIZE"`; `_try_scratch_mount "-o compress=no,compress-force=no" 2> /dev/null`. The core workload then performs these representative operations: `_btrfs subvolume create $SCRATCH_MNT/subv1`; `_btrfs subvolume create $SCRATCH_MNT/subv2`; `_btrfs subvolume create $SCRATCH_MNT/subv3`; `_btrfs quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | $SED_PROG -n '/[0-9]/p' | \`; `$XFS_IO_PROG -f -c "pwrite 0 256K" $SCRATCH_MNT/subv1/file1 | _filter_xfs_io`; `cp --reflink $SCRATCH_MNT/subv1/file1 $SCRATCH_MNT/subv2/file1`; `cp --reflink $SCRATCH_MNT/subv1/file1 $SCRATCH_MNT/subv3/file1`. The workload is mostly sequential, so failure attribution is tied to the exact command that exits non-zero.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, cp --reflink support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/091 -->
