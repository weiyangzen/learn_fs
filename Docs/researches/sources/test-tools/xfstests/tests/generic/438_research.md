# sources/test-tools/xfstests/tests/generic/438

## Purpose
This is a regression test for kernel patch "ext4: Fix data corruption for mmap writes" The problem this test checks for is when too much is zeroed in the tail page that gets written out just while the file gets extended and written to through mmap. Based on test program by Michael Zimmer <michael@swarm64.com>. It is registered as generic/438 with `_begin_fstest` tags `auto, mmap`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include FILE=$TEST_DIR/testfile_fallocate, SYNCPID=$!. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "t_mmap_fallocate".

External/helper commands: $XFS_IO_PROG, rm.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
