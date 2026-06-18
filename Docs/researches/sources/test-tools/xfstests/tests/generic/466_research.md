# sources/test-tools/xfstests/tests/generic/466

## Purpose
Check that high-offset reads and writes work. It is registered as generic/466 with `_begin_fstest` tags `auto, quick, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include devsize=$(blockdev --getsize64 $SCRATCH_DEV). Topic focus: general filesystem semantics. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; unmounts the scratch filesystem; writes deterministic byte patterns.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_block_device $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, mkdir, mount, stat, truncate.

Representative `xfs_io` operations: truncate $len; pread -v -q $bigoff 1.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
