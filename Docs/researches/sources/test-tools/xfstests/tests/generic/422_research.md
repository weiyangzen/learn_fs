# sources/test-tools/xfstests/tests/generic/422

## Purpose
Test that a filesystem's implementation of the stat(2) system call reports correct values for the number of blocks allocated for a file when there are delayed allocations. It is registered as generic/422 with `_begin_fstest` tags `auto, quick, prealloc`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: space_used. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions space_used.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch; _require_xfs_io_command "falloc" "-k"; _require_odirect.

External/helper commands: $XFS_IO_PROG, diff, du, touch, truncate.

Representative `xfs_io` operations: pwrite -S 0xaa 0 64K; truncate 128K; falloc -k 0 128K; pwrite -S 0xff 0 64K; pwrite -S 0xff 64K 64K; pwrite -S 0x20 64K 64K; pwrite -S 0xab 0 64K; pwrite -S 0xef 0 64K.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 65536/65536 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 65536/65536 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 65536/65536 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
