<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/041 -->
# sources/test-tools/xfstests/tests/btrfs/041

## Purpose
Test that btrfs-progs' restore command is able to correctly recover files that have compressed extents, specially when the respective file extent items have a non-zero data offset field. Btrfs-progs: fix restore of files with compressed extents The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, and its main coverage is: Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `test_btrfs_restore` fstest tags: `auto`, `quick`, `compress` requirement gates: `_require_test`, `_require_scratch`. The important external command surfaces are `_btrfs restore $SCRATCH_DEV $restore_dir` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xff -b 100000 0 100000" -c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0xaa -b 100000 100000 100000" -c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0x1e -b 2 10000 2" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xd0 -b 11 33000 11" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xbc -b 100 99000 100" $SCRATCH_MNT/foo \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount $OPTIONS`; `_scratch_unmount`. The core workload then performs these representative operations: `_btrfs restore $SCRATCH_DEV $restore_dir`; `$XFS_IO_PROG -f -c "pwrite -S 0xff -b 100000 0 100000" -c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0xaa -b 100000 100000 100000" -c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0x1e -b 2 10000 2" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xd0 -b 11 33000 11" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xbc -b 100 99000 100" $SCRATCH_MNT/foo \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `md5sum $restore_dir/foo | cut -d ' ' -f 1`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`.

## State and Persistence Behavior
Uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/041 -->
