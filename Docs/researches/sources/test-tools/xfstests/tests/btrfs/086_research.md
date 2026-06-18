<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/086 -->
# sources/test-tools/xfstests/tests/btrfs/086

## Purpose
Test cloning a file range with a length of zero into a destination offset greater than zero. This made btrfs create an extent state record with a start offset greater than the end offset, resulting in chaos such as an infinite loop when evicting an inode. This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$CLONER_PROG -s 0 -d 65536 -l 0 $SCRATCH_MNT/foo $SCRATCH_MNT/bar` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$CLONER_PROG -s 0 -d 65536 -l 0 $SCRATCH_MNT/foo $SCRATCH_MNT/bar`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/086 -->
