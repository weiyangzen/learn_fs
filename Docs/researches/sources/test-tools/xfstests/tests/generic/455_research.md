# sources/test-tools/xfstests/tests/generic/455

## Purpose
Run fsx with log writes to verify power fail safeness. It is registered as generic/455 with `_begin_fstest` tags `auto, log, replay, recoveryloop`, making it part of the crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, check_files. Important state variables and paths include SANITY_DIR=$TEST_DIR/fsxtests, size=$(_small_fs_size_mb 200), devsize=$((1024*1024*size / 512)), csize=$((1024*64 / 512)), lowspace=$((1024*1024 / 512)), NUM_FILES=4, NUM_OPS=200, FSX_OPTS=-N $NUM_OPS -d -P $SANITY_DIR -i $LOGWRITES_DMDEV, seeds=(0 0 0 0), test_md5=(). Topic focus: crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency. Key helper behavior includes: requires a journal/log capable filesystem before crash replay; sets up dm-thin backing storage; captures block writes for replay testing.

## Control Flow
operates in the configured test filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, check_files.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/dmlogwrites, common/dmthin, common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch_nocheck; _require_no_logdev; _require_log_writes; _require_dm_target thin-pool; _require_metadata_journaling "$LOGWRITES_DMDEV".

External/helper commands: $FSX_PROG, find, grep, md5sum, mkdir, rm, umount.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
