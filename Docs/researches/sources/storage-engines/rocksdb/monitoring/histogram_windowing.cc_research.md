# sources/storage-engines/rocksdb/monitoring/histogram_windowing.cc

Purpose: Implements a time-windowed histogram that keeps aggregate statistics for the most recent N windows and expires older buckets lazily from the Add hot path.

Important APIs/types/functions: Constructors allocate `window_stats_` and set default or configured window counts/durations. `Add` calls `TimerTick`, updates aggregate `stats_`, and updates the current window. `Merge` combines compatible windowed histograms. `SwapHistoryBucket` expires the next circular bucket and advances `current_window_`.

Control flow: `TimerTick` compares `clock_->NowMicros()` with `last_swap_time_` and requires the current window to have at least `min_num_per_window_` samples. `SwapHistoryBucket` uses `try_lock` so only one racing writer rotates windows. It subtracts dropped bucket counts and aggregate sums, recomputes min/max if the dropped bucket owned them, clears the expired bucket, and stores the next index.

State and dependencies: Maintains an aggregate `HistogramStat`, a circular array of `HistogramStat`, clock pointer, mutex, and relaxed atomic current-window/last-swap state. It depends on `SystemClock`, base histogram code, and cast utilities.

Risks/test signals: Add can land samples in the older bucket during rotation, explicitly tolerated by comments. Merge first merges total stats even if window configuration is incompatible, then returns before aligning window buckets, so callers can observe aggregate merge without window compatibility. Tests cover expiration and merge behavior under mock time.
