<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/037 -->
# sources/test-tools/xfstests/tests/btrfs/037

## Purpose
Test for a btrfs data corruption when using compressed files/extents. Under certain cases, it was possible for reads to return random data caused partial updates to those regions that were supposed to be filled with zeroes to save random (and invalid) data into the file extents. This is fixed by the commit for the linux kernel titled: The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, `prealloc`, and its main coverage is: Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `compress`, `prealloc` requirement gates: `_require_scratch`, `_require_xfs_io_command`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0x06 -b 18670 266978 18670" \`; `$XFS_IO_PROG -c "falloc 26450 665194" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "truncate 542872" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; `MD5=`md5sum $SCRATCH_MNT/foobar | cut -f 1 -d ' '`` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount "-o compress-force=lzo"`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; `_scratch_mount "-o ro"`; plus 1 more source-matched operations. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0x06 -b 18670 266978 18670" \`; `$XFS_IO_PROG -c "falloc 26450 665194" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "truncate 542872" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; `MD5=`md5sum $SCRATCH_MNT/foobar | cut -f 1 -d ' '``. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; `for i in `seq 1 27``.

## State and Persistence Behavior
Uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io subcommand availability, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/037 -->
