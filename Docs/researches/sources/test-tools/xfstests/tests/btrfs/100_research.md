<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/100 -->
# sources/test-tools/xfstests/tests/btrfs/100

## Purpose
Test device replace works when the source device has EIO The script is categorized by `_begin_fstest` as `auto`, `replace`, `volume`, `eio`, `raid`, and its main coverage is: Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. I/O error injection through device-mapper targets to validate degraded multi-device behavior.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `replace`, `volume`, `eio`, `raid` requirement gates: `_require_scratch_dev_pool`, `_require_dm_target`. The important external command surfaces are `_btrfs filesystem show -m $SCRATCH_MNT`; `$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT | _filter_btrfs_filesystem_show`; `error_devid=`$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT |\`; `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"`; `_btrfs replace start -B $error_devid $dev2 $SCRATCH_MNT`; plus 2 more source-matched operations for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_dmerror_cleanup`; `_dmerror_init`; `_dmerror_mount`; `_dmerror_load_error_table`. The core workload then performs these representative operations: `_btrfs filesystem show -m $SCRATCH_MNT`; `$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT | _filter_btrfs_filesystem_show`; `error_devid=`$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT |\`; `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"`; `_btrfs replace start -B $error_devid $dev2 $SCRATCH_MNT`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_run_fsstress -d $SCRATCH_MNT -n 200 -p 8 -x "$snapshot_cmd" -X 50`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on multi-device scratch pool, device-mapper target support, btrfs-progs command wrappers, Btrfs-specific output filters, dm-error I/O failure simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/100 -->
