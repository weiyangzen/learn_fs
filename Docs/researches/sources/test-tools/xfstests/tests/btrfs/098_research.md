<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/098 -->
# sources/test-tools/xfstests/tests/btrfs/098

## Purpose
Test that if we fsync a file that got one extent partially cloned into a lower file offset, after a power failure our file has the same content it had before the power failure and after the extent cloning operation. The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, `clone`, `log`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior. Fsync log tree replay and power-failure simulation through dm-flakey to verify durable metadata and checksum recovery.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `metadata`, `clone`, `log` requirement gates: `_require_scratch`, `_require_dm_target`, `_require_cloner`, `_require_metadata_journaling`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((200 * $BLOCK_SIZE)) $((25 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $(((200 * $BLOCK_SIZE) + (5 * $BLOCK_SIZE))) \`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_cleanup_flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_flakey_drop_and_remount`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((200 * $BLOCK_SIZE)) $((25 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $(((200 * $BLOCK_SIZE) + (5 * $BLOCK_SIZE))) \`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, device-mapper target support, btrfs clone ioctl exerciser, xfs_io data-shaping commands, dm-flakey crash simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/098 -->
