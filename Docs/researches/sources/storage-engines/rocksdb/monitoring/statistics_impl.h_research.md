# sources/storage-engines/rocksdb/monitoring/statistics_impl.h

Purpose: Declares `StatisticsImpl`, the built-in RocksDB implementation of the public `Statistics` interface, along with helper functions for recording stats.

Important APIs/types/functions: Internal enum sentinels extend public ticker/histogram maxima. `StatisticsImpl` overrides ticker, histogram, reset, map, string, and option-related APIs. Nested `StatisticsData` stores cache-line-aligned per-core tickers and histograms with custom aligned allocation. Inline helpers `RecordInHistogram`, `RecordTimeToHistogram`, `RecordTick`, and `SetTickerCount` null-check before dispatch.

Control flow/integration: Writers use per-core storage for low contention; readers and reset operations use `aggregate_lock_`. The class can wrap an inner `Statistics` object for forwarding and is registered as `"BasicStatistics"`.

State and dependencies: Depends on `HistogramImpl`, `CoreLocalArray`, RocksDB statistics APIs, port alignment, likely macros, and mutex utilities.

Risks/test signals: The `StatisticsData` size/alignment static assertion is disabled under `TEST_CACHE_LINE_SIZE`. If public enum maxima change, arrays and map tests catch mismatches. Optional inner stats can duplicate work and must tolerate forwarding.
