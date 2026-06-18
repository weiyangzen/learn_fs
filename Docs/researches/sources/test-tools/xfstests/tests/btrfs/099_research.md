<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/099 -->
# sources/test-tools/xfstests/tests/btrfs/099

## Purpose
Check for qgroup reserved space leaks caused by re-writing dirty ranges The script is categorized by `_begin_fstest` as `auto`, `quick`, `qgroup`, `limit`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `qgroup`, `limit` requirement gates: `_require_scratch`, `_require_btrfs_qgroup_report`, `_require_fs_space`. The important external command surfaces are `_btrfs quota enable $SCRATCH_MNT`; `_btrfs qgroup limit $FILESIZE 0/5 $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -b $BLOCKSIZE 0 $(($FILESIZE / 4))" \`; `$XFS_IO_PROG -f -c "pwrite -b $BLOCKSIZE 0 $(($FILESIZE - $BLOCKSIZE))" \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `_btrfs quota enable $SCRATCH_MNT`; `_btrfs qgroup limit $FILESIZE 0/5 $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -b $BLOCKSIZE 0 $(($FILESIZE / 4))" \`; `$XFS_IO_PROG -f -c "pwrite -b $BLOCKSIZE 0 $(($FILESIZE - $BLOCKSIZE))" \`. It also uses background or repeated stress/control loops: `_scratch_mkfs >> $seqres.full 2>&1`; `for i in `seq 1 5`; do`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, qgroup reporting support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/099 -->
