# sources/test-tools/xfstests/tests/generic/406

## Purpose
If a larger dio write (size >= 128M) got splitted, the assertion in endio would complain (CONFIG_BTRFS_ASSERT is required). Regression test for Btrfs: adjust outstanding_extents counter properly when dio write is split. It is registered as generic/406 with `_begin_fstest` tags `auto, quick`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include blocksize=$(( (128 + 1) * 2 * 1024 * 1024)), fsblock=$(( (128 + 1) * 2 * 1024)). Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_odirect; _require_fs_space $SCRATCH_MNT $fsblock.

External/helper commands: $XFS_IO_PROG.

Representative `xfs_io` operations: pwrite -b ${blocksize} 0 ${blocksize}.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
