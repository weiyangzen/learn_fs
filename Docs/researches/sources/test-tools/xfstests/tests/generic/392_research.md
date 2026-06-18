# sources/test-tools/xfstests/tests/generic/392

## Purpose
Test inode's metadata after fsync or fdatasync calls. In the case of fsync, filesystem should recover all the inode metadata, while recovering for fdatasync it should at least recovery i_size. It is registered as generic/392 with `_begin_fstest` tags `shutdown, auto, quick, metadata, punch`, making it part of the crash recovery/log replay, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: check_inode_metadata, test_i_size, test_i_time, test_punch. Important state variables and paths include testfile=$SCRATCH_MNT/testfile. Topic focus: crash recovery/log replay, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; requires a journal/log capable filesystem before crash replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions check_inode_metadata, test_i_size, test_i_time, test_punch.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/punch.

Prerequisite gates: _require_scratch; _require_scratch_shutdown; _require_xfs_io_command "fpunch"; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, rm, stat, touch, truncate.

Representative `xfs_io` operations: $sync_mode; truncate 4M; pwrite 0 4M; fsync; pwrite 4M $2; truncate 4202496; pwrite 0 4202496; fpunch 4194304 $2.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: ==== i_size 1024 test with fsync ====; ==== i_size 4096 test with fsync ====; ==== i_time test with fsync ====; ==== fpunch 1024 test with fsync ====; ==== fpunch 4096 test with fsync ====; ==== i_size 1024 test with fdatasync ====. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
