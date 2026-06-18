<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/055 -->
# sources/test-tools/xfstests/tests/btrfs/055

## Purpose
Regression test for the btrfs ioctl clone operation when the source range contains hole(s) and the FS has the NO_HOLES feature enabled (file holes don't need file extent items in the btree to represent them). The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `test_btrfs_clone_with_holes` fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`, `_require_btrfs_fs_feature`, `_require_btrfs_mkfs_feature`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -s -f -c "pwrite -S 0x01 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x02 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x04 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x05 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0xff -b $EXTENT_SIZE 0 $EXTENT_SIZE" \`; `$CLONER_PROG -s $((2 * $BLOCK_SIZE)) -d 0 -l $((6 * $BLOCK_SIZE)) \`; plus 15 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs "$1" >/dev/null 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -s -f -c "pwrite -S 0x01 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x02 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x04 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x05 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0xff -b $EXTENT_SIZE 0 $EXTENT_SIZE" \`; `$CLONER_PROG -s $((2 * $BLOCK_SIZE)) -d 0 -l $((6 * $BLOCK_SIZE)) \`; `od -t x1 $SCRATCH_MNT/bar | _filter_od`; `$CLONER_PROG -s $((5 * $BLOCK_SIZE)) -d $((8 * $BLOCK_SIZE)) \`; `$CLONER_PROG -s 0 -d $((16 * $BLOCK_SIZE)) -l $((5 * $BLOCK_SIZE)) \`; `$XFS_IO_PROG -c "truncate $((16 * $BLOCK_SIZE))" $SCRATCH_MNT/foo \`; plus 11 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs "$1" >/dev/null 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/055 -->
