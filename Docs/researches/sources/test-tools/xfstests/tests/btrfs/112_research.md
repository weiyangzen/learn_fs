<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/112 -->
# sources/test-tools/xfstests/tests/btrfs/112

## Purpose
Test several cases of cloning inline extents that used to lead to file corruption or data loss. The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, `prealloc`, `compress`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone. I/O error injection through device-mapper targets to validate degraded multi-device behavior.

## Important APIs, Types, and Functions
local shell functions: `test_cloning_inline_extents` fstest tags: `auto`, `quick`, `clone`, `prealloc`, `compress` requirement gates: `_require_scratch`, `_require_cloner`, `_require_btrfs_fs_feature`, `_require_btrfs_mkfs_feature`, `_require_xfs_io_command`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 50" $SCRATCH_MNT/bar \`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 16K" $SCRATCH_MNT/foo \`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/bar $SCRATCH_MNT/foo \`; `od -t x1 $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0xcc 0 100" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xdd 4K 12K" $SCRATCH_MNT/foo2 \`; plus 16 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount $mount_opts`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 50" $SCRATCH_MNT/bar \`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 16K" $SCRATCH_MNT/foo \`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/bar $SCRATCH_MNT/foo \`; `od -t x1 $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0xcc 0 100" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xdd 4K 12K" $SCRATCH_MNT/foo2 \`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/bar $SCRATCH_MNT/foo2 \`; `od -t x1 $SCRATCH_MNT/foo2`; `$XFS_IO_PROG -c "pwrite -S 0xee 0 90" $SCRATCH_MNT/foo2 | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0x01 0 40" $SCRATCH_MNT/foo4 \`; plus 12 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs $mkfs_opts >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io subcommand availability, xfs_io data-shaping commands, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/112 -->
