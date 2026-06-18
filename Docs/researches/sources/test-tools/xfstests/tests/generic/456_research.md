# sources/test-tools/xfstests/tests/generic/456

## Purpose
This test is motivated by a bug found in ext4 during random crash consistency tests. Fixed by commit 51e3ae81ec58 ("ext4: fix interaction between i_size, fallocate, and delalloc after a crash") This is also a regression test for ext4 bug that zero range can beyond i_disksize and fixed by commit 801674f34ecf ("ext4: do not zeroout extents beyond i_disksize"). It is registered as generic/456 with `_begin_fstest` tags `auto, quick, metadata, collapse, zero, prealloc`, making it part of the crash recovery/log replay, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include fsxops=$tmp.fsxops. Topic focus: crash recovery/log replay, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_xfs_io_command "falloc"; _require_dm_target flakey; _require_xfs_io_command "falloc" "-k"; _require_xfs_io_command "fzero"; _require_xfs_io_command "fcollapse"; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $FSX_PROG, fallocate, rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
