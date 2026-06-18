# sources/test-tools/xfstests/tests/generic/460

## Purpose
Test that XFS reserves reasonable indirect blocks for delalloc and speculative allocation, and doesn't cause any fdblocks corruption. This was inspired by an XFS but that too large 'indlen' was returned by xfs_bmap_worst_indlen() which can't fit in a 17 bits value (STARTBLOCKVALBITS is defined as 17), then leaked 1 << 17 blocks in sb_fdblocks. This was only seen on XFS with rmapbt feature enabled, but nothing prevents the test from being a generic test. It is registered as generic/460 with `_begin_fstest` tags `auto, quick, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: save_dirty_ratio, set_dirty_ratio, restore_dirty_ratio, _cleanup. Important state variables and paths include testfile=$SCRATCH_MNT/1G_file.$seq, file_size=$((1024 * 1024 * 1024)), saved_dirty_background_ratio=0, saved_dirty_ratio=0. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions save_dirty_ratio, set_dirty_ratio, restore_dirty_ratio, _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_fs_space $SCRATCH_MNT $((1024 * 1024)).

External/helper commands: $XFS_IO_PROG, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
