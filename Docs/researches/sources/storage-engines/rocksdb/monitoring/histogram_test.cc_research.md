# sources/storage-engines/rocksdb/monitoring/histogram_test.cc

Purpose: Unit tests for `HistogramImpl` and `HistogramWindowingImpl` statistics behavior, including percentile math, merging, clearing, expiration, and standard deviation edge cases.

Important APIs/types/functions: `PopulateHistogram` inserts ranges into a histogram while advancing a `MockSystemClock`. Helper assertions `BasicOperation`, `MergeHistogram`, `EmptyHistogram`, and `ClearHistogram` are reused against both plain and windowed histograms. Tests include `HistogramWindowingExpire`, `HistogramWindowingMerge`, `LargeStandardDeviation`, and `LostUpdateStandardDeviation`.

Control flow: Tests populate deterministic distributions, call `Data`, and assert median, p95, p99, average, min/max, and counts with small tolerances. Windowing tests configure three one-second windows, inject a mock clock, and verify old windows are dropped as time advances.

State/dependencies: Uses `MockSystemClock`, RocksDB test harness, and `Random` to simulate microsecond passage. The global mock clock is injected into windowed histograms through `TEST_UpdateClock`.

Risks/test signals: The suite documents tolerated lock-free races: `LostUpdateStandardDeviation` manually corrupts sum-of-squares to ensure standard deviation never goes negative or NaN. It does not stress multi-threaded races directly, but it covers the expected mathematical outputs.
