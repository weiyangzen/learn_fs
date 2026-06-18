# sources/storage-engines/rocksdb/monitoring/histogram.cc

Purpose: Implements RocksDB histogram buckets and statistical summaries used by `StatisticsImpl` histograms and other monitoring paths.

Important APIs/types/functions: `HistogramBucketMapper` constructs 109 human-readable bucket upper bounds by repeatedly multiplying by 1.5 and rounding to two significant digits. `HistogramStat` implements `Clear`, `Add`, `Merge`, percentile, average, standard deviation, `Data`, and `ToString`. `HistogramImpl` wraps `HistogramStat` behind the abstract `Histogram` interface and a mutex for clear/merge.

Control flow: `Add` locates a bucket, updates bucket count, min, max, count, sum, and sum-of-squares using relaxed atomics. `Merge` compares min/max with CAS loops and fetch-adds aggregate fields. Percentiles scan cumulative bucket counts, linearly interpolate inside the selected bucket, and clamp to current min/max.

State and dependencies: State is atomic counters in `HistogramStat`; `HistogramImpl` adds a mutex for operations that need multi-field coordination. It depends on `port/port.h`, `util/cast_util.h`, `<cmath>`, and `rocksdb/statistics.h`.

Risks/test signals: `Add` intentionally uses load/store increments instead of `fetch_add`, so racing increments can be lost; tests explicitly tolerate this for standard deviation but guard against negative/NaN variance. Min/max updates are relaxed and approximate under races. The fixed bucket array size in the header must match the mapper bucket count.
