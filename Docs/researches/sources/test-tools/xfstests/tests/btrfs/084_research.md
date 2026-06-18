<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/084 -->
# sources/test-tools/xfstests/tests/btrfs/084

## Purpose
Test for incremental send where the difference between the parent and send snapshots is that for a subtree with the same path in both snapshots (p1/p2), the root directories were swapped. This issue was fixed by the following linux kernel btrfs patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fssum replay must match original snapshot manifests Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/084 -->
