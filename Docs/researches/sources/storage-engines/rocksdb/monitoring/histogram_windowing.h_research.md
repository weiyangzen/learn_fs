# sources/storage-engines/rocksdb/monitoring/histogram_windowing.h

Purpose: Declares `HistogramWindowingImpl`, a `Histogram` implementation that reports only a sliding time-window of samples.

Important APIs/types/functions: The class implements the full `Histogram` interface, exposes constructors for default and custom `(num_windows, micros_per_window, min_num_per_window)`, and provides debug-only `TEST_UpdateClock` for deterministic time tests.

Control flow/integration: Public read APIs proxy to the aggregate `stats_`. Writes go through `Add`, which may rotate windows. `Merge` supports combining another `HistogramWindowingImpl`. It is intended as a drop-in histogram where recent-window behavior is preferable to all-time aggregation.

State and persistence behavior: State is in-memory: a shared `SystemClock`, mutex, aggregate `HistogramStat`, circular `window_stats_`, atomic `current_window_`, and atomic `last_swap_time_`. No data is persisted directly.

Dependencies: Depends on `monitoring/histogram.h` and forward-declares `SystemClock`.

Risks/test signals: The class deletes copy/assignment because it owns mutable atomic/statistical arrays. Configuration comments contain a typo (`configuable`) but the contract is clear. `histogram_test.cc` validates expiration, merge, clear, empty, and standard operations.
