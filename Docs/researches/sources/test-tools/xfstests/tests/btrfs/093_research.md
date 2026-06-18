<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/093 -->
# sources/test-tools/xfstests/tests/btrfs/093

## Purpose
Test btrfs file range cloning with the same file as a source and destination. This tests a specific scenario where the extent layout of the file confused the clone ioctl implementation making it return -EEXIST to userspace. This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
local shell functions: `test_clone` fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((2 * $bs)) $((2 * $bs))" \`; `$CLONER_PROG -s $((3 * $bs)) -d $((267 * $bs)) -l 0 $SCRATCH_MNT/foo \`; `$CLONER_PROG -s $((217 * $bs)) -d $((95 * $bs)) -l 0 $SCRATCH_MNT/foo \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `$CLONER_PROG -s $((3 * $bs)) -d $((267 * $bs)) -l 0 $SCRATCH_MNT/a \`; `$CLONER_PROG -s $((217 * $bs)) -d $((95 * $bs)) -l 0 $SCRATCH_MNT/b \`; plus 2 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs "-O ^no-holes -n $bs" >>$seqres.full 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`; `_scratch_mkfs "-O no-holes -n $bs" >>$seqres.full 2>&1`; plus 1 more source-matched operations. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((2 * $bs)) $((2 * $bs))" \`; `$CLONER_PROG -s $((3 * $bs)) -d $((267 * $bs)) -l 0 $SCRATCH_MNT/foo \`; `$CLONER_PROG -s $((217 * $bs)) -d $((95 * $bs)) -l 0 $SCRATCH_MNT/foo \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `$CLONER_PROG -s $((3 * $bs)) -d $((267 * $bs)) -l 0 $SCRATCH_MNT/a \`; `$CLONER_PROG -s $((217 * $bs)) -d $((95 * $bs)) -l 0 $SCRATCH_MNT/b \`; `md5sum $SCRATCH_MNT/foo2 | _filter_scratch`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs "-O ^no-holes -n $bs" >>$seqres.full 2>&1`; `_scratch_mkfs "-O no-holes -n $bs" >>$seqres.full 2>&1`.

## State and Persistence Behavior
Uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/093 -->
