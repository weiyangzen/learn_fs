# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/VerifyChecksumsTest.java

## Purpose

This suite verifies that `ReadOptions.setVerifyChecksums` controls read-time block checksum verification for iteration and get paths, using the `BLOCK_CHECKSUM_COMPUTE_COUNT` ticker as a proxy.

## Important APIs and types

The file uses `RocksDB`, `Statistics`, `TickerType.BLOCK_CHECKSUM_COMPUTE_COUNT`, `Options.setStatistics`, `ReadOptions`, `FlushOptions`, `RocksIterator`, and an abstract nested `Operations` template.

## Control flow

`Operations` generates 10,000 keys, sorts expected iteration order, fills the DB, and defines read modes for get, multi-get, and iteration with configured `ReadOptions`. `verifyChecksums` writes and flushes data, reopens the DB repeatedly, runs operations with verify false/true/false/true, and compares checksum ticker counts before and after each run.

## State and persistence behavior

The DB is written, flushed, closed, and reopened so reads come from persisted table files. The statistics object persists across reopen loops and accumulates checksum ticker state until changed by reads.

## Dependencies and integration points

This connects Java `ReadOptions` to the native table read path, statistics tickers, flush/reopen behavior, and iterator/get APIs.

## Risks and test signals

Risks include ticker noise from non-read operations, optimized multi-get not updating the ticker, randomness in selected get keys, and timing-independent but environment-sensitive counts. Signals are unchanged checksum count when verification is false and increased count when true. The multi-get test is ignored because its optimized path does not reliably update the ticker.
