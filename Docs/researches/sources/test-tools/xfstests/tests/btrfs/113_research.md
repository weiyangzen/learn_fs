<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/113 -->
# sources/test-tools/xfstests/tests/btrfs/113

## Purpose
Test that truncating a file that consists of a compressed and inlined extent to a smaller size and then cloning it into another file is not possible and does not result in leaking stale data (data past the truncation offset) nor losing data in the clone operation's destination file. The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `compress`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xa1 0 128" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 256" $SCRATCH_MNT/bar | _filter_xfs_io`; `$XFS_IO_PROG -c "truncate 128" $SCRATCH_MNT/foo`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/foo $SCRATCH_MNT/bar \`; `od -t x1 $SCRATCH_MNT/bar` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o compress"`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xa1 0 128" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 256" $SCRATCH_MNT/bar | _filter_xfs_io`; `$XFS_IO_PROG -c "truncate 128" $SCRATCH_MNT/foo`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/foo $SCRATCH_MNT/bar \`; `od -t x1 $SCRATCH_MNT/bar`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/113 -->
