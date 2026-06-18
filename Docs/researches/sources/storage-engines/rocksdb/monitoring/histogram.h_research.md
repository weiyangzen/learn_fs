# sources/storage-engines/rocksdb/monitoring/histogram.h

Purpose: Declares the histogram abstraction and concrete statistical storage used by RocksDB monitoring and statistics reporting.

Important APIs/types/functions: `HistogramBucketMapper` maps values to bucket indexes and exposes limits/counts. `HistogramStat` stores min, max, count, sum, sum squares, and a fixed atomic bucket array. `Histogram` is the abstract interface for clearing, adding, merging, querying percentiles, formatting, and exporting `HistogramData`. `HistogramImpl` is the standard implementation with `TEST_GetStats()`.

Control flow/integration: The header separates lock-free hot-path `HistogramStat::Add` from higher-level `HistogramImpl` API calls. `StatisticsImpl` embeds one `HistogramImpl` per histogram type per core, merges them for reads, and calls `Data`/`ToString`.

State and persistence behavior: Histograms are in-memory only. No persistence is performed here, but exported `HistogramData` and `ToString` can be consumed by stats dumps and persistent stats logic elsewhere.

Dependencies: Uses `<atomic>` transitively through atomics, `<mutex>`, `<vector>`, `<string>`, and `rocksdb/statistics.h`.

Risks/test signals: The comments and fixed `buckets_[109]` are a maintenance contract with `HistogramBucketMapper`. Copy/assignment are deleted to avoid unsafe duplication of atomic state. Tests in `histogram_test.cc` cover basic distribution math, empty/clear behavior, merge, boundary values, and race-tolerant standard deviation.
