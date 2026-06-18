# sources/storage-engines/tikv/components/tikv_util/src/metrics/metrics_reader.rs

## Purpose
Provides a small helper for reading the average value newly recorded into a Prometheus `Histogram` since the previous read.

## Important APIs, Types, and Functions
- `HistogramReader { histogram, sum, count }` stores a histogram handle and the last observed sum/count.
- `HistogramReader::new(histogram)` snapshots the initial sum and count.
- `read_latest_avg` returns `(new_sum - old_sum) / (new_count - old_count)` or `0.0` if no new samples arrived.

## Control Flow
Each read fetches current histogram sum and count. If count is unchanged, the previous baseline is retained and zero is returned. Otherwise the delta average is computed and the stored baseline is advanced.

## State and Persistence Behavior
State is local to the reader instance and reflects the last successful read. It does not persist across process restarts and does not reset the underlying histogram.

## Dependencies and Integration Points
Uses `prometheus::Histogram`. It is re-exported from `metrics/mod.rs` for components that want interval averages without separately tracking counters.

## Risks
The helper assumes histogram sum/count are monotonic. If the histogram is reset or replaced, deltas can become misleading. Concurrent observations are fine, but concurrent reads of the same `HistogramReader` require external synchronization.

## Test Signals
No direct unit tests; expected behavior is simple delta arithmetic over Prometheus histogram accessors.
