# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/read.rs

## Purpose
This file defines a broad suite of e2e performance counter tests and benchmarks for file reads. It covers empty files, small files, large multi-block/tree files, reads from the middle, reads past EOF, nested and deeply nested file paths, repeated reads from one file handle, and optional release after read.

## Important APIs, types, and functions
- Registers twenty-two cases via `perf_test!`, each instantiated with `CLOSE_AFTER` false and true.
- Uses `FilesystemDriver::create_and_open_file`, `write`, `read`, and optional `release` through `maybe_close`.
- Uses `BLOCKSIZE_BYTES` and `NUM_BYTES_FOR_THREE_LEVEL_TREE` to construct files that exercise single-block and multi-level blob trees.
- Uses `NumBytes` for offsets and lengths and `AtimeUpdateBehavior` to compute expected timestamp-write costs.
- Expected counts use exact `ActionCounts` values with fixture-specific branches and `close_after`/`expect_atime_update` multipliers.

## Control flow
Each test creates a new filesystem, creates and opens a file during setup, optionally writes initial data, then reads a specific range. EOF tests assert an empty result for at least the small-file beyond-EOF case. Large-file cases create data spanning multiple internal tree levels and read either one byte or a tree-sized region. `multiple_reads_from_same_file` performs ten one-byte reads from adjacent positions. If `CLOSE_AFTER` is true, the file handle is released after reading.

## State and persistence behavior
Read operations generally load file metadata/data but do not modify content. Atime updates are modeled as deferred work that only appears in many cases when the handle is released: expected writes, resizes, stores, and flushes are multiplied by `close_after`. Empty-file reads use a different atime formula than non-empty reads: the file itself notes a TODO asking why its atime calculations differ from other operations. Setup writes are flushed/reset before the measured read unless the shared harness keeps deliberate file handles open.

## Dependencies and integration points
The suite depends heavily on the shared fixture's artificial block sizing. `BLOCKSIZE_BYTES` and `NUM_BYTES_FOR_THREE_LEVEL_TREE` make tree-depth costs deterministic, which lets the expected `HLActionCounts::store_load` and `LLActionCounts::load` values distinguish single-block, multi-block, and beyond-EOF traversals. It integrates with both fuser variants and fuse-mt through `FixtureType`, and with all atime policies expanded by the performance macro.

## Risks and observations
The file contains a top-level TODO warning that atime formulas differ from `readlink` and even among read cases. Many branches attribute fuser-without-cache overhead to repeated path lookup. Since reads optionally include release, some expected counts combine read traversal with close-time flush and atime persistence. The exact high-level counts for large and repeated reads are brittle because they encode the current tree implementation and cache reuse pattern.

## Test signals
The suite validates several important performance contracts: reading an empty file performs minimal data traversal; reading beyond EOF returns no data and avoids full-range traversal; large middle reads load many high-level blocks; repeated small reads reuse some low-level state but still count repeated blob reads; path depth mainly penalizes fuser without inode cache; and atime writes are expected only under the configured policies and mostly when the file is closed.
