<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/031 -->
# sources/test-tools/xfstests/tests/btrfs/031

## Purpose
Testing cross-subvolume sparse copy on btrfs - Create two subvolumes, mount one of them - Create a file on each (sub/root)volume, reflink them on the other volumes - Change one original and two reflinked files - Move reflinked files between subvolumes The script is categorized by `_begin_fstest` as `auto`, `quick`, `subvol`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_checksum_files` fstest tags: `auto`, `quick`, `subvol`, `clone` requirement gates: `_require_test`, `_require_scratch`, `_require_cp_reflink`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume create $subvol1 >> $seqres.full`; `$BTRFS_UTIL_PROG subvolume create $subvol2 >> $seqres.full`; `_mount -t btrfs -o subvol=subvol-$seq-1 $SCRATCH_DEV $cross_mount_test_dir` for Btrfs control and `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 10' $testdir1/file1 \`; `$XFS_IO_PROG -f -c 'pwrite -S 0x62 0 13000' $cross_mount_test_dir/file2 \`; `$XFS_IO_PROG -f -c 'pwrite -S 0x63 0 17000' $subvol2/file3 \`; `cp --reflink=always $testdir1/file1 $subvol1`; `cp --reflink=always $testdir1/file1 $subvol2`; `cp --reflink=always $subvol1/file2 $testdir1/`; plus 6 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume create $subvol1 >> $seqres.full`; `$BTRFS_UTIL_PROG subvolume create $subvol2 >> $seqres.full`; `_mount -t btrfs -o subvol=subvol-$seq-1 $SCRATCH_DEV $cross_mount_test_dir`; `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 10' $testdir1/file1 \`; `$XFS_IO_PROG -f -c 'pwrite -S 0x62 0 13000' $cross_mount_test_dir/file2 \`; `$XFS_IO_PROG -f -c 'pwrite -S 0x63 0 17000' $subvol2/file3 \`; `cp --reflink=always $testdir1/file1 $subvol1`; `cp --reflink=always $testdir1/file1 $subvol2`; `cp --reflink=always $subvol1/file2 $testdir1/`; `cp --reflink=always $subvol1/file2 $subvol2`; plus 5 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs > /dev/null 2>&1`.

## State and Persistence Behavior
Uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, cp --reflink support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/031 -->
