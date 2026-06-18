# sources/storage-engines/rocksdb/db/db_statistics_test.cc

## Purpose

This file validates RocksDB statistics counters and histograms for compression, mutex wait timing, reset semantics, stats-level exclusions, checksum verification reads, block checksum accounting, and bytes-written accounting for normal and transactional writes.

## Important APIs, Types, And Functions

- `DBStatisticsTest` derives from `DBTestBase`.
- Tests use `CreateDBStatistics`, `Statistics::set_stats_level`, `getTickerCount`, `getAndResetTickerCount`, `histogramData`, and `Statistics::Reset`.
- Compression tests iterate `GetSupportedCompressions`, configure block-based tables with uncompressed indexes, and inspect compression/decompression tickers.
- Mutex tests use `ThreadStatusUtil::TEST_SetStateDelay`.
- Checksum tests use `VerifyFileChecksums`, `VerifyChecksum`, `GetFileChecksumGenCrc32cFactory`, file corruption helpers, and checksum-related tickers.
- Transaction write accounting uses `TransactionDB`, `TxnDBWritePolicy::WRITE_COMMITTED`, `Transaction::Prepare`, `Transaction::Commit`, and `WriteBatchInternal::kHeader`.

## Control Flow

`CompressionStatsTest` loops over supported compression algorithms except no-compression and bzip2, writes compressible values, flushes, and checks compressed block counts and byte estimates. It then reads all keys to trigger decompression stats. The test reopens with random incompressible values to verify compression-rejected counters, then reopens with `kNoCompression` to verify compression-bypassed counters.

Mutex wait tests create a DB with statistics, inject artificial mutex wait delay, and show that default stats levels do not count `DB_MUTEX_WAIT_MICROS` while `StatsLevel::kAll` does. `ResetStats` checks an arbitrary ticker and histogram before and after `Put`, then calls `Reset` and verifies counters return to zero. `ExcludeTickers` switches between excluding tickers and allowing ticker collection.

Checksum tests separate WAL-only data from SST-backed data. `VerifyChecksumReadStat` expects no verify-read bytes before flush, exact file-size reads for `VerifyFileChecksums`, and at least file size for block-level `VerifyChecksum`. `BlockChecksumStats` checks block checksum compute/mismatch counters, then corrupts a table data block and expects one mismatch.

`BytesWrittenStats` compares `WAL_FILE_BYTES` and `BYTES_WRITTEN` for ordinary writes, then recreates the DB as `TransactionDB` with and without pipelined writes. It verifies `Prepare` writes WAL bytes but not `BYTES_WRITTEN`, while `Commit` makes total WAL bytes equal memtable bytes plus one write-batch header.

## State And Persistence Behavior

The tests persist SST files via flushes, reset or recreate DBs to isolate statistic windows, corrupt an SST on disk, and recreate as `TransactionDB` for transactional persistence behavior. Counters live in the shared `Statistics` object attached to `Options`, so reopen/reset boundaries are part of the test design.

## Dependencies And Integration Points

This file connects monitoring/statistics, compression managers/codecs, block-based table building/reading, checksum verification, thread status instrumentation, transaction DB WAL/memtable paths, write-batch encoding, and file corruption helpers. It depends on stable block counts for the chosen block size and generated value lengths.

## Risks And Edge Cases

Compression counts are approximate for byte totals but exact for expected block counts; codec behavior changes can shift counts. BZip2 is skipped due to known odd behavior. Checksum counters intentionally bypass `PerfLevel` and must remain populated even with perf disabled. Transaction write accounting is guarding against double-counting issue patterns; WAL headers make exact equality non-obvious.

## Test Signals

Signals are ticker values, reset ticker deltas, histogram maxima, checksum status, corrupted-file mismatch counts, and transactional WAL-versus-memtable byte relationships. Assertions use both exact equality and tolerance macros where compression byte estimates vary.
