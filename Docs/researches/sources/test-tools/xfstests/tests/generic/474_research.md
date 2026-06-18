# sources/test-tools/xfstests/tests/generic/474

## Purpose
Inspired by syncfs bug of overlayfs which does not sync dirty inodes in underlying filesystem. Create a small file then run syncfs and shutdown filesystem(or underlying filesystem of overlayfs) to check syncfs result. Test will be skipped if filesystem(or underlying filesystem of overlayfs) does not support shutdown. It is registered as generic/474 with `_begin_fstest` tags `auto, quick, shutdown, metadata`, making it part of the writeback error reporting, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include localdir=$SCRATCH_MNT/dir. Topic focus: writeback error reporting, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_fssum; _require_scratch; _require_scratch_shutdown; _require_xfs_io_command "syncfs".

External/helper commands: $XFS_IO_PROG, mkdir.

Representative `xfs_io` operations: pwrite 0 4K.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: OK. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
