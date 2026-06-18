# sources/test-tools/xfstests/tests/generic/457

## Purpose
Run fsx with log writes on cloned files to verify power fail safeness. It is registered as generic/457 with `_begin_fstest` tags `auto, log, replay, clone, recoveryloop`, making it part of the reflink/shared extents, crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, check_files. Important state variables and paths include SANITY_DIR=$TEST_DIR/fsxtests, size=$(_small_fs_size_mb 200), devsize=$((1024*1024*size / 512)), csize=$((1024*64 / 512)), lowspace=$((1024*1024 / 512)), NUM_FILES=10, NUM_OPS=10, FSX_OPTS=-N $NUM_OPS -d -k -P $SANITY_DIR -i $LOGWRITES_DMDEV, test_md5=(). Topic focus: reflink/shared extents, crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency. Key helper behavior includes: sets up dm-thin backing storage; captures block writes for replay testing; requires reflink support on scratch.

## Control Flow
operates in the configured test filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, check_files.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/dmlogwrites, common/dmthin, common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_test; _require_scratch_reflink; _require_no_logdev; _require_cp_reflink; _require_log_writes; _require_dm_target thin-pool.

External/helper commands: $FSX_PROG, $XFS_IO_PROG, find, grep, md5sum, mkdir, rm, umount.

Representative `xfs_io` operations: pwrite -S 0xff 0 256k; fsync.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; device-mapper setup, replay ordering, or host capabilities can dominate failures; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
