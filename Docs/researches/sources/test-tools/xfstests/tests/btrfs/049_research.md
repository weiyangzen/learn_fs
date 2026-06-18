<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/049 -->
# sources/test-tools/xfstests/tests/btrfs/049

## Purpose
Ensure that it's possible to add a device when we have a paused balance and the filesystem is mounted with skip_balance. The issue is fixed by a patch titled "btrfs: allow device add if balance is paused" The script is categorized by `_begin_fstest` as `quick`, `balance`, `auto`, and its main coverage is: Multi-device balance stress, including mutual exclusion with replace/delete operations and post-stress scrub/fsck validation. Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `check_exclusive_ops` fstest tags: `quick`, `balance`, `auto` requirement gates: `_require_scratch_swapfile`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG device remove 2 $SCRATCH_MNT &>/dev/null`; `$BTRFS_UTIL_PROG filesystem resize -5m $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG replace start -B 2 $SPARE_DEV $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG balance pause "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG balance status "$SCRATCH_MNT" | grep -q paused`; `$BTRFS_UTIL_PROG device add -K -f $SPARE_DEV "$SCRATCH_MNT"`; plus 4 more source-matched operations for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs >/dev/null`; `_scratch_mount`; `_scratch_cycle_mount "skip_balance"`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG device remove 2 $SCRATCH_MNT &>/dev/null`; `$BTRFS_UTIL_PROG filesystem resize -5m $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG replace start -B 2 $SPARE_DEV $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG balance pause "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG balance status "$SCRATCH_MNT" | grep -q paused`; `$BTRFS_UTIL_PROG device add -K -f $SPARE_DEV "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG balance resume "$SCRATCH_MNT" &>/dev/null`; plus 3 more source-matched operations. It also uses background or repeated stress/control loops: `$BTRFS_UTIL_PROG device remove 2 $SCRATCH_MNT &>/dev/null`; `$BTRFS_UTIL_PROG filesystem resize -5m $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG replace start -B 2 $SPARE_DEV $SCRATCH_MNT &> /dev/null`; `swapon "$swapfile" &> /dev/null`; `_run_fsstress $args >>$seqres.full`; `$BTRFS_UTIL_PROG balance resume "$SCRATCH_MNT" &>/dev/null`; plus 2 more source-matched operations.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/049 -->
