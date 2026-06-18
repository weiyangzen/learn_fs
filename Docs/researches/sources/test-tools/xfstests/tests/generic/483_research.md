# sources/test-tools/xfstests/tests/generic/483

## Purpose
Test that fsync operations preserve extents allocated with fallocate(2) that are placed beyond a file's size. It is registered as generic/483 with `_begin_fstest` tags `auto, quick, log, metadata, fiemap, prealloc`, making it part of the crash recovery/log replay, preallocation/range operations, fiemap/bmap reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, preallocation/range operations, fiemap/bmap reporting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble, common/punch.

Prerequisite gates: _require_scratch; _require_dm_target flakey; _require_xfs_io_command "falloc" "-k"; _require_xfs_io_command "fiemap"; _require_metadata_journaling $SCRATCH_DEV; _require_congruent_file_oplen $SCRATCH_MNT 262144.

External/helper commands: $XFS_IO_PROG, rm, stat, truncate.

Representative `xfs_io` operations: pwrite -S 0xea 0 256K; pwrite -S 0xcf $offset 4K; pwrite -S 0xf1 0 256K; falloc -k 256K 768K; fsync; falloc -k 256K 1M; truncate 256K; falloc -k 1M 2M; fiemap -v.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: File foo fiemap:; 0: [0..2559]: extent; File foo size:; 262144; File bar fiemap:; 0: [0..2559]: extent. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
