# sources/storage-engines/foundationdb/contrib/grv_proxy_model/rate_model.py

## Purpose
`rate_model.py` provides simple rate sources for the GRV proxy simulator. These models supply request rates or ratekeeper limits as functions of simulated time.

## Important APIs, Types, And Functions
`RateModel.get_rate(time)` is the base interface. `FixedRateModel(rate)` returns a constant; `UnlimitedRateModel` intends to represent an effectively unbounded rate of `1e9`; `IntervalRateModel(intervals)` stores sorted `(start_time, rate)` pairs and returns the active interval; `SawtoothRateModel(low, high, frequency)` alternates between low and high rates; `DistributionRateModel(distribution, frequency)` samples a rate from a callable and holds it for a frequency window.

## Control Flow
Consumers call `get_rate` at simulated times. Fixed and unlimited models return stored values. Interval lookup returns zero before the first interval, scans for the interval preceding the requested time, truncates older intervals from `self.intervals`, and returns the current rate. Sawtooth uses `int(2 * time / frequency) % 2` to alternate. Distribution refreshes when no prior sample exists or when the time has moved to a new frequency bucket.

## State And Persistence Behavior
Rates are in-memory only. `IntervalRateModel` mutates `self.intervals` by discarding prior intervals, so it assumes monotonic time. `DistributionRateModel` stores `last_change` and `rate`, making it stateful and also monotonic-time-oriented. Nothing is persisted.

## Dependencies And Integration Points
The module imports `numpy` for random distribution call sites, though only `DistributionRateModel` receives callables. `ratekeeper_model.py` and `workload_model.py` instantiate these classes in predefined scenarios.

## Risks And Edge Cases
`UnlimitedRateModel.__init__` sets `self.rate` without calling `FixedRateModel.__init__`, but the effect is equivalent for current fields. `IntervalRateModel` gives incorrect answers for non-monotonic time after truncating previous intervals. `SawtoothRateModel` divides by `frequency`; zero frequency is not guarded. `DistributionRateModel` uses a bucket comparison that is sensitive to the meaning of `last_change`, not just absolute bucket number.

## Test Signals
Tests should cover fixed and unlimited returns, interval boundaries, pre-first-interval zero behavior, monotonic interval truncation, sawtooth phase changes, zero-rate handling, and seeded distribution refresh cadence.
