<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/104 -->
# sources/test-tools/xfstests/tests/btrfs/104

## Purpose
Test btrfs quota group consistency operations during snapshot delete. Btrfs has had long standing issues with drop snapshot failing to properly account for quota groups. This test crafts several snapshot trees with shared and exclusive elements. One of the trees is removed and then quota group consistency is checked. The script is categorized by `_begin_fstest` as `auto`, `qgroup`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `qgroup` requirement gates: `_require_scratch`, `_require_btrfs_qgroup_report`. The important external command surfaces are `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume snapshot $SCRATCH_MNT/snap1 $SCRATCH_MNT/snap2`; `_btrfs quota enable $SCRATCH_MNT`; `_btrfs subvolume delete $SCRATCH_MNT/snap1`; `_btrfs filesystem sync $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 4095" $loc/file$i > /dev/null 2>&1`; `$XFS_IO_PROG -f -c "pwrite 0 128k" $loc/extentfile > /dev/null 2>&1` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs "--nodesize 16384" >> $seqres.full 2>&1`; `_scratch_mount`; `_scratch_cycle_mount`. The core workload then performs these representative operations: `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume snapshot $SCRATCH_MNT/snap1 $SCRATCH_MNT/snap2`; `_btrfs quota enable $SCRATCH_MNT`; `_btrfs subvolume delete $SCRATCH_MNT/snap1`; `_btrfs filesystem sync $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite 0 4095" $loc/file$i > /dev/null 2>&1`; `$XFS_IO_PROG -f -c "pwrite 0 128k" $loc/extentfile > /dev/null 2>&1`. It also uses background or repeated stress/control loops: `for i in `seq -w 1 $n`; do`; `$XFS_IO_PROG -f -c "pwrite 0 4095" $loc/file$i > /dev/null 2>&1`; `$XFS_IO_PROG -f -c "pwrite 0 128k" $loc/extentfile > /dev/null 2>&1`; `_scratch_mkfs "--nodesize 16384" >> $seqres.full 2>&1`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; forces transaction or file-log persistence with sync/fsync; mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, qgroup reporting support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
explicit filesystem check must pass fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/104 -->
