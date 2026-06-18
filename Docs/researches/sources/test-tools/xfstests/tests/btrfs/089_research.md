<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/089 -->
# sources/test-tools/xfstests/tests/btrfs/089

## Purpose
Test deleting the default subvolume, making sure that submounts under it are not unmounted prematurely. This is a regression test for Linux commit "Btrfs: don't invalidate root dentry when subvolume deletion fails". The script is categorized by `_begin_fstest` as `auto`, `quick`, `subvol`, and its main coverage is: Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `subvol` requirement gates: `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume set-default $testvol_id "$SCRATCH_MNT" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume delete "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume set-default $testvol_id "$SCRATCH_MNT" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume delete "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume set-default $testvol_id "$SCRATCH_MNT" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume delete "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/089 -->
