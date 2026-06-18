# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/write.rs

## Purpose
This file defines a large performance counter matrix for file writes. It measures small and large writes to empty, small, and large files; writes in the middle versus beyond end; nested path overhead; repeated writes to the same open handle; and the effect of closing/releasing the file after the write.

## Important APIs, Types, and Functions
The `write` group registers generic scenario instantiations for `<false>` and `<true>` `CLOSE_AFTER` variants. Scenarios call `fixture.filesystem.write(file.clone(), &mut fh, NumBytes::from(offset), data)` and then `maybe_close::<CLOSE_AFTER, _>(fixture, file, fh).await`.

Setup uses `create_and_open_file`, initial `write` calls, `mkdir`, and `mkdir_recursive`. Important constants are `BLOCKSIZE_BYTES` for small multi-block files and `NUM_BYTES_FOR_THREE_LEVEL_TREE` for large block-tree coverage.

## Control Flow
Each scenario opens a file during setup and returns `(node, file_handle)` to the counted phase. The counted phase writes a vector of bytes at a chosen offset, optionally releases the handle, and asserts counts. Large write scenarios allocate or overwrite block-tree regions. `multiple_writes_to_same_file` performs ten one-byte writes around the large-tree offset before optional close.

## State and Persistence Behavior
Writes mutate in-memory/open-handle state and persistent file data. Without `CLOSE_AFTER`, many scenarios avoid flush and resize counts at the blobstore layer, indicating dirty state remains associated with the open file. With close, counts add release-time loads, writes, resizes, blob flushes, and high-level `store_flush_block`. Writes beyond EOF allocate holes/new blocks and record `store_create`; overwrites record `store_overwrite`; repeated writes show high-level repeated loads/data access but only one low-level store unless closed.

## Dependencies and Integration Points
The file depends on `maybe_close` from `utils.rs`, `FilesystemDriver`, `ActionCounts`, `FixtureType`, `NumBytes`, path types, and all storage counter structures. It is closely related to release/fsync/ftruncate performance tests and relies on the test driver to reset setup counts before measuring the write under test.

## Risks and Notes
The expected counts are highly sensitive to cache, writeback, sparse-file, and release semantics. `CLOSE_AFTER` arithmetic is manually encoded in each expected count block and can hide mistakes if release behavior changes. Many TODO comments remain around expected counts, and fuser-without-inode-cache often doubles loads relative to other fixtures.

## Test Signals
The suite covers allocation, overwrite, sparse extension, open-handle writeback, close-triggered flush behavior, nested lookup overhead, and repeated-write cache behavior. Exact counts across false/true close variants are the primary regression signal.
