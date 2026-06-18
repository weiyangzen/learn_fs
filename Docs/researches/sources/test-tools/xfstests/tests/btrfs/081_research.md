<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/081 -->
# sources/test-tools/xfstests/tests/btrfs/081

## Purpose
Regression test for a btrfs clone ioctl issue where races between a clone operation and concurrent target file reads would result in leaving stale data in the page cache. After the clone operation finished, reading from the clone target file would return the old and no longer valid data. This affected only buffered reads (i.e. didn't affect direct IO reads). This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
local shell functions: `create_source_file`, `create_target_file`, `reader_loop` fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG \`; `$XFS_IO_PROG -f -c "pwrite -S 0xff 0 $file_size" \`; `$CLONER_PROG -s 0 -d 0 -l $(($num_extents * $extent_size)) \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/bar | _filter_scratch`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_cycle_mount`. The core workload then performs these representative operations: `$XFS_IO_PROG \`; `$XFS_IO_PROG -f -c "pwrite -S 0xff 0 $file_size" \`; `$CLONER_PROG -s 0 -d 0 -l $(($num_extents * $extent_size)) \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/bar | _filter_scratch`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `for ((i = 0; i < $num_extents; i++)); do`; `trap "wait; exit" SIGTERM`; `while true; do`; `_scratch_mkfs >>$seqres.full 2>&1`; `reader_loop "bar" &`; `kill $reader_pid > /dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/081 -->
