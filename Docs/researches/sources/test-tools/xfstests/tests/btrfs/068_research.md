<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/068 -->
# sources/test-tools/xfstests/tests/btrfs/068

## Purpose
Run btrfs subvolume create/mount/umount/delete and remount with different compress algorithms simultaneously, with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `subvol`, `remount`, `compress`, `scrub`, `raid`, and its main coverage is: Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `subvol`, `remount`, `compress`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `if [ ! -z "$stop_file" ] && [ ! -z "$subvol_pid" ] && \`; `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_subvolume $SCRATCH_DEV $SCRATCH_MNT subvol_$$ $subvol_mnt $stop_file >/dev/null 2>&1 &`; `_btrfs_stress_remount_compress $SCRATCH_MNT >/dev/null 2>&1 &`; plus 4 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/068 -->
