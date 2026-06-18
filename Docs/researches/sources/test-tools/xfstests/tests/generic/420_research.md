# sources/test-tools/xfstests/tests/generic/420

## Purpose
Verify fallocate(mode=FALLOC_FL_KEEP_SIZE|FALLOC_FL_PUNCH_HOLE) does not alter the file size. It is registered as generic/420 with `_begin_fstest` tags `auto, quick, punch`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile=${TEST_DIR}/testfile.$seq. Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command fpunch.

External/helper commands: $XFS_IO_PROG, fallocate, grep, stat.

Representative `xfs_io` operations: pwrite -b 2048 0 2048; fpunch 2048 2048; stat.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Testing fallocate(mode=FALLOC_FL_KEEP_SIZE|FALLOC_FL_PUNCH_HOLE); wrote 2048/2048 bytes at offset 0; stat.size = 2048. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
