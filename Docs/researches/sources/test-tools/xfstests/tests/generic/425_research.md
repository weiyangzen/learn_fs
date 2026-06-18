# sources/test-tools/xfstests/tests/generic/425

## Purpose
Check that FIEMAP produces some output when we require an external block to hold extended attributes. It is registered as generic/425 with `_begin_fstest` tags `auto, quick, attr, fiemap`, making it part of the extended attributes, fiemap/bmap reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, testfile=$testdir/attrfile, blk_sz=$(_get_file_block_size $SCRATCH_MNT), max_attrs=$((2 * blk_sz / 20)), i=0, f1=$(_count_attr_extents $testfile). Topic focus: extended attributes, fiemap/bmap reporting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; persists extended-attribute namespace/value state; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_attrs; _require_xfs_io_command "fiemap" "-a".

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, $XFS_IO_PROG, attr, mkdir, mount, rm, touch.

Representative `xfs_io` operations: fiemap -a -v.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create the original files; Check attr extent counts; Check attr extent counts after remount. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
