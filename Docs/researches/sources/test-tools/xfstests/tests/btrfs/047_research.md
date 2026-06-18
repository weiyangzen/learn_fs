<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/047 -->
# sources/test-tools/xfstests/tests/btrfs/047

## Purpose
Test that we can't set xattrs on subvolume placeholder directories. Regression test for Btrfs: disable xattr operations on subvolume directories. The script is categorized by `_begin_fstest` as `auto`, `quick`, `snapshot`, `attr`, and its main coverage is: Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `snapshot`, `attr` requirement gates: `_require_attrs`, `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/parent" >>$seqres.full`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/parent/child" >>$seqres.full`; `$BTRFS_UTIL_PROG subvolume snapshot "$SCRATCH_MNT/parent" "$SCRATCH_MNT/snapshot" >>$seqres.full`; `$BTRFS_UTIL_PROG filesystem sync "$SCRATCH_MNT" >>$seqres.full` for Btrfs control and `$SETFATTR_PROG -n user.test -v foo "$SCRATCH_MNT/snapshot/child" |& _filter_scratch` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/parent" >>$seqres.full`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/parent/child" >>$seqres.full`; `$BTRFS_UTIL_PROG subvolume snapshot "$SCRATCH_MNT/parent" "$SCRATCH_MNT/snapshot" >>$seqres.full`; `$BTRFS_UTIL_PROG filesystem sync "$SCRATCH_MNT" >>$seqres.full`; `$SETFATTR_PROG -n user.test -v foo "$SCRATCH_MNT/snapshot/child" |& _filter_scratch`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; `$SETFATTR_PROG -n user.test -v foo "$SCRATCH_MNT/snapshot/child" |& _filter_scratch`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on extended attribute tooling, scratch filesystem lifecycle helpers, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/047 -->
