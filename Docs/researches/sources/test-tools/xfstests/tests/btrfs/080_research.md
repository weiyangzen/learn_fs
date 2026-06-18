<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/080 -->
# sources/test-tools/xfstests/tests/btrfs/080

## Purpose
Regression test for a btrfs issue where if right after the snapshot creation ioctl started, a file write followed by a file truncate happened, with both operations increasing the file's size, the created snapshot would capture an inconsistent state of the file system tree. That state reflected the file truncation but it didn't reflect the write operation, and left a gap between two file extent items (and that gap corresponded to the total or a partial area of the write operation's range). This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `snapshot`, and its main coverage is: Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `create_snapshot`, `create_file`, `workout` fstest tags: `auto`, `snapshot` requirement gates: `_require_scratch_nocheck`. The important external command surfaces are `_btrfs subvolume snapshot -r \` for Btrfs control and `run_check $XFS_IO_PROG -f \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs -O list-all 2>&1 | grep -q '\bno-holes\b'`; `_scratch_mkfs "$mkfs_options" >>$seqres.full 2>&1`; `_scratch_mount`; `_check_scratch_fs`. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r \`; `run_check $XFS_IO_PROG -f \`. It also uses background or repeated stress/control loops: `kill $p &> /dev/null`; `create_file $name &`; `create_snapshot &`; `wait $fpid`; `wait $spid`; `_scratch_mkfs -O list-all 2>&1 | grep -q '\bno-holes\b'`; plus 7 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached digest output before and after remount/receive must match expected content explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/080 -->
