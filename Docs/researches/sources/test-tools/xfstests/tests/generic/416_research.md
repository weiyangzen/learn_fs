# sources/test-tools/xfstests/tests/generic/416

## Purpose
Test fs behavior when large write request can't be met by one single extent Inspired by a bug in a btrfs fix, which doesn't get exposed by current test cases. It is registered as generic/416 with `_begin_fstest` tags `auto, enospc`, making it part of the preallocation/range operations, ENOSPC/free-space handling, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: fill_fs. Important state variables and paths include fs_size=$((128 * 1024 * 1024)), page_size=$(_get_page_size), nr_files=$(($fs_size / $page_size)). Topic focus: preallocation/range operations, ENOSPC/free-space handling, filename/directory semantics. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions fill_fs.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch.

External/helper commands: $XFS_IO_PROG, dd, rm.

Representative `xfs_io` operations: pwrite 0 $(($fs_size / 8)).

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 16777216/16777216 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
