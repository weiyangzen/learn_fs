<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/059 -->
# sources/test-tools/xfstests/tests/btrfs/059

## Purpose
Regression test for btrfs where removing the flag FS_COMPR_FL (chattr -c) from an inode wouldn't clear its compression property. This was fixed in the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, and its main coverage is: Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `compress` requirement gates: `_require_test`, `_require_scratch`, `_require_btrfs_command`, `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`. The important external command surfaces are `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir compression | \`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir/file1 compression | \`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir/file2 compression | \`; plus 2 more source-matched operations for Btrfs control and `$CHATTR_PROG +c $SCRATCH_MNT/testdir`; `$CHATTR_PROG -c $SCRATCH_MNT/testdir` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir compression | \`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir/file1 compression | \`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir/file2 compression | \`; `$CHATTR_PROG +c $SCRATCH_MNT/testdir`; `$CHATTR_PROG -c $SCRATCH_MNT/testdir`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >> $seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, specific btrfs-progs subcommand availability, btrfs-progs command wrappers, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/059 -->
