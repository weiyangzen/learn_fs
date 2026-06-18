# sources/storage-engines/rocksdb/db/db_rate_limiter_test.cc

## Purpose

This file tests how RocksDB routes read, flush, compaction, WAL write, and explicit WAL flush I/O through `RateLimiter` accounting. It is not testing throttling latency directly; it verifies that the correct APIs attach rate-limiter priorities and that requests are charged to the expected `Env::IOPriority` buckets.

## Important APIs, Types, And Functions

- `DBRateLimiterOnReadTest` derives from `DBTestBase` and `WithParamInterface<std::tuple<bool, bool, bool>>`, parameterizing direct reads, block cache, and readahead.
- `GetOptions()` enables `RateLimiter::Mode::kAllIo`, `FileChecksumGenCrc32cFactory`, block-based tables, optional direct reads, and disabled automatic compaction.
- `GetReadOptions()` sets `ReadOptions::rate_limiter_priority = Env::IO_USER` and optionally sets `readahead_size`.
- Read APIs under test include `DB::Get`, both newer pointer-array `MultiGet` and older vector-returning `MultiGet`, `NewIterator`, `VerifyChecksum`, and `VerifyFileChecksums`.
- `DBRateLimiterOnWriteTest` uses `RateLimiter::Mode::kWritesOnly` and checks flush and compaction priority buckets.
- `DBRateLimiterOnWriteWALTest` parameterizes `WriteOptions::disableWAL`, `Options::manual_wal_flush`, and `WriteOptions::rate_limiter_priority`.
- `DBRateLimiterOnManualWALFlushTest` checks `FlushWALOptions::rate_limiter_priority` in manual WAL flush mode.

## Control Flow

The read fixture initializes three one-key SST files, moves them to level 1, then measures `options_.rate_limiter->GetTotalRequests(...)` before and after reads. `Get` expects one rate-limited read per first key lookup and no repeated request when block cache is enabled. `MultiGet` builds stable key buffers and slices, performs batch reads, and checks status success plus aggregate IO_USER charging. Iterator tests assert forward scans increment request counts per file/block and account for cache reuse on reverse scans. Checksum tests deliberately exercise full-table verification and raw file checksum verification, with platform/direct-IO-specific expected counts.

The write tests create overlapping files, then verify flushes charge `Env::IO_HIGH` and compaction charges `Env::IO_LOW`. WAL tests separate automatic WAL flush behavior from manual WAL flush behavior. Automatic WAL rate limiting is valid only when WAL is enabled, manual WAL flush is disabled, and priority is `Env::IO_USER`; invalid combinations must return `InvalidArgument` with an explanatory message. Manual WAL flush tests confirm writes themselves do not rate-limit WAL when `manual_wal_flush` is enabled and that `DB::FlushWAL` controls charging.

## State And Persistence Behavior

The tests persist real SST and WAL files in DBTestBase-managed directories. Read tests rely on file placement and block cache state to distinguish first reads from cached reads. Checksum tests persist CRC32c file checksums and verify rate-limited file reads. Write tests persist L0 files, compact them into L1, and inspect `FilesPerLevel` as a state signal. WAL tests persist WAL records and, depending on manual or automatic flush mode, expect rate-limiter counters to be unchanged or incremented.

## Dependencies And Integration Points

The file integrates with `db/db_test_util.h`, `rocksdb/db.h`, `rocksdb/env.h`, `util/file_checksum_helper.h`, block-based table factory configuration, direct-IO capability checks, and the generic rate limiter. It is sensitive to table reader behavior, block cache behavior, checksum verification implementation, WAL flushing semantics, and IO priority conventions used by flush/compaction/WAL code.

## Risks And Edge Cases

Direct IO is skipped when unsupported, so platform coverage differs. Exact request counts depend on block-based table read patterns, tail prefetching, readahead, block cache residency, and Windows-specific prefetch behavior. The old and new `MultiGet` APIs are intentionally both covered because they use different internal read paths. WAL priority validation is strict; new priorities or WAL mode changes can break these tests even if user-visible writes still work.

## Test Signals

Primary signals are exact `GetTotalRequests` deltas by `Env::IO_USER`, `Env::IO_HIGH`, `Env::IO_LOW`, and `Env::IO_TOTAL`, `ASSERT_OK`/`InvalidArgument` status checks, and `FilesPerLevel` assertions around compaction. The test binary installs stack traces and runs all gtest cases from `main`.
