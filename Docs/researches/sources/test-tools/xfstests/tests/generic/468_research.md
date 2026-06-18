# sources/test-tools/xfstests/tests/generic/468

## Purpose
This testcase is a fallocate variant of generic/392, it expands to test block preallocation functionality of fallocate. In this case, we are trying to execute: 1. fallocate {,-k} 2. f{data,}sync 3. power-cuts 4. recovery filesystem during mount 5. check inode's metadata In the case of fsync, filesystem should recover all the inode metadata, while recovering i_blocks and i_size at least for fdatasync, so this testcase excepts that inode metadata will be unchanged after recovery. It is registered as generic/468 with `_begin_fstest` tags `shutdown, auto, quick, metadata, prealloc`, making it part of the crash recovery/log replay, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: check_inode_metadata, test_falloc. Important state variables and paths include testfile=$SCRATCH_MNT/testfile. Topic focus: crash recovery/log replay, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; requires a journal/log capable filesystem before crash replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions check_inode_metadata, test_falloc.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_scratch_shutdown; _require_xfs_io_command "falloc" "-k"; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, rm, stat, truncate.

Representative `xfs_io` operations: $sync_mode; truncate 4202496; pwrite 0 4202496; fsync; falloc $2 4202496 $3.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: ==== falloc 1024 test with fsync ====; ==== falloc 4096 test with fsync ====; ==== falloc 104857600 test with fsync ====; ==== falloc -k 1024 test with fsync ====; ==== falloc -k 4096 test with fsync ====; ==== falloc -k 104857600 test with fsync ====. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
