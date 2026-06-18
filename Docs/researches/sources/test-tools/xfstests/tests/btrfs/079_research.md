<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/079 -->
# sources/test-tools/xfstests/tests/btrfs/079

## Purpose
Do write along with fiemap ioctl. Regression test for the kernel comit: 51f395ad btrfs: Use right extent length when inserting overlap extent map. When calling fiemap(without SYNC flag) and btrfs fs is commiting, it will cause race condition and cause btrfs to generate a wrong extent whose len is overflow and fail to insert into the extent map tree, returning -EEXIST. The script is categorized by `_begin_fstest` as `auto`, `rw`, `metadata`, `fiemap`, `prealloc`, and its main coverage is: Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `dd_work`, `_filter_error`, `fiemap_work` fstest tags: `auto`, `rw`, `metadata`, `fiemap`, `prealloc` requirement gates: `_require_scratch`, `_require_command`, `_require_xfs_io_command`, `_require_fs_space`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `_require_command "$FILEFRAG_PROG" filefrag`; `$XFS_IO_PROG -f -c "falloc 0 $filesize" $testfile`; `dd if=/dev/zero of=$out bs=$buffersize count=$count \`; `$FILEFRAG_PROG $filename 2> $tmp.output 1> /dev/null` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `_require_command "$FILEFRAG_PROG" filefrag`; `$XFS_IO_PROG -f -c "falloc 0 $filesize" $testfile`; `dd if=/dev/zero of=$out bs=$buffersize count=$count \`; `$FILEFRAG_PROG $filename 2> $tmp.output 1> /dev/null`. It also uses background or repeated stress/control loops: `kill $dd_pid &> /dev/null`; `kill $fiemap_pid &> /dev/null`; `wait`; `_scratch_mkfs >>$seqres.full 2>&1`; `conv=notrunc &> /dev/null`; `trap "wait; exit" SIGTERM`; plus 7 more source-matched operations.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io subcommand availability, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/079 -->
