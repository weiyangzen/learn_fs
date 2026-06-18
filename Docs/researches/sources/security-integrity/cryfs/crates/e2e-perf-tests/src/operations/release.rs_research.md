# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/release.rs

## Purpose
This file defines e2e performance counter tests and benchmarks for releasing open file handles. It covers unchanged files and files with pending writes, across empty, small, large, nested, deeply nested, overwrite, append/beyond-EOF, and sparse-extension scenarios.

## Important APIs, types, and functions
- Registers fifteen release cases through `perf_test!`.
- Uses `FilesystemDriver::create_and_open_file`, `write`, and `release`.
- Uses `test_noflush` for the measured release so the harness does not add an extra post-test cache reset after release.
- Uses `setup_noflush` for pending-write cases so writes remain dirty and are flushed by the measured release.
- Uses `BLOCKSIZE_BYTES`, `NUM_BYTES_FOR_THREE_LEVEL_TREE`, and `NumBytes` to choose offsets and sizes that exercise direct blocks and larger tree structures.

## Control flow
Unchanged cases create/open a file, sometimes write and flush setup data, then measure only `release(file, fh)`. Dirty cases create/open a file, optionally write initial data in normal setup, then perform a second write in `setup_noflush` so the measured release flushes it. Cases vary whether the write is to an empty file, middle of existing data, beyond EOF, large range, nested path, or deeply nested path.

## State and persistence behavior
Release is the persistence boundary for open file handles. Unchanged releases still flush the open file and may load metadata, but generally do not store new low-level blocks. Dirty releases write blob data, resize metadata, and flush dirty blocks. Writes beyond EOF often expect two low-level stores, reflecting data plus metadata/sparse extension behavior. Nested and deeply nested dirty releases show extra lookup/read-all costs for fuser without inode cache, while fuser with cache and fuse-mt generally keep release costs flat once the file handle is available.

## Dependencies and integration points
The suite is coupled to the file-cache and flush semantics implemented by `FilesystemDriver::release`, to the fixture's `test_noflush` behavior, and to the block/blob tree layout controlled by fixture constants. It integrates with the tracking blobstore/high-level/low-level blockstores to observe flushes and stores, and with fixture types to distinguish cached node handles from repeated path resolution.

## Risks and observations
The file starts with TODOs noting suspicious behavior: some releases load low-level blocks below the cache, simple flushes have many high-level operations, and some release-after-write cases lack expected low-level stores. Individual cases also ask why noatime can still produce two stores. These are high-value regression tests but also brittle: changing writeback, sparse-file, or release flushing logic will invalidate many exact counts.

## Test signals
The suite checks that unchanged release has a minimal flush profile, that large unchanged files load more high-level blocks than small unchanged files, that dirty release persists pending writes, that middle writes are cheaper than beyond-EOF extension in low-level stores, and that fuser without inode cache pays additional path-resolution costs in nested cases. Benchmarks expose release latency for clean and dirty handles.
