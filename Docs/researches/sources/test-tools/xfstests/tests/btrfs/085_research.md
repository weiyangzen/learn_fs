<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/085 -->
# sources/test-tools/xfstests/tests/btrfs/085

## Purpose
Tests to ensure that orphan items are properly created and cleaned up on next mount. There are three cases where orphan items may be cleaned up: 1) Default subvolume is fs tree root (mkfs default) 2) Default subvolume is explicitly created subvolume 3) Non-default subvolume lookup The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, `subvol`, and its main coverage is: Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `has_orphan_item`, `test_orphan`, `new_subvolume`, `new_default` fstest tags: `auto`, `quick`, `metadata`, `subvol` requirement gates: `_require_scratch`, `_require_dm_target`, `_require_btrfs_command`. The important external command surfaces are `if $BTRFS_UTIL_PROG inspect-internal dump-tree $SCRATCH_DEV | \`; `_btrfs subvolume create $SCRATCH_MNT/testdir`; `SUB=$($BTRFS_UTIL_PROG subvolume list $SCRATCH_MNT | $AWK_PROG '{print $2}')`; `_btrfs subvolume set-default $SUB $SCRATCH_MNT` for Btrfs control and `run_check dd if=/dev/zero of=$TESTPATH bs=$SIZE count=1` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_cleanup_flakey`; `_scratch_mkfs >> $seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_load_flakey_table $FLAKEY_DROP_WRITES`; `_scratch_unmount`; `_load_flakey_table $FLAKEY_ALLOW_WRITES`; plus 5 more source-matched operations. The core workload then performs these representative operations: `if $BTRFS_UTIL_PROG inspect-internal dump-tree $SCRATCH_DEV | \`; `_btrfs subvolume create $SCRATCH_MNT/testdir`; `SUB=$($BTRFS_UTIL_PROG subvolume list $SCRATCH_MNT | $AWK_PROG '{print $2}')`; `_btrfs subvolume set-default $SUB $SCRATCH_MNT`; `run_check dd if=/dev/zero of=$TESTPATH bs=$SIZE count=1`. It also uses background or repeated stress/control loops: `_scratch_mkfs >> $seqres.full 2>&1`; `exec 27>&-`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, device-mapper target support, specific btrfs-progs subcommand availability, btrfs-progs command wrappers, dm-flakey crash simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/085 -->
