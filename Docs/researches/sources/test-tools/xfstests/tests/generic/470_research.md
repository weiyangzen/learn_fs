# sources/test-tools/xfstests/tests/generic/470

## Purpose
Use dm-log-writes to verify that MAP_SYNC actually syncs metadata during page faults. It is registered as generic/470 with `_begin_fstest` tags `auto, quick, dax, mmap`, making it part of the fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include MAPPED_LEN=$((512 * 1024 * 1024)), LEN=$((1024 * 1024)). Topic focus: fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; captures block writes for replay testing.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/dmlogwrites, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_no_logdev; _require_log_writes_dax_mountopt "dax"; _require_xfs_io_command "mmap" "-S"; _require_xfs_io_command "log_writes"; _require_command "$BLKDISCARD_PROG" blkdiscard.

External/helper commands: $XFS_IO_PROG, du, rm, truncate.

Representative `xfs_io` operations: truncate $LEN; mmap -S 0 $LEN; mwrite 0 $LEN; log_writes -d $LOGWRITES_NAME -m preunmap.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: 1.0M SCRATCH_MNT/test. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
