# sources/storage-engines/foundationdb/contrib/grv_proxy_model/smoother.py

## Purpose
`smoother.py` implements an exponential smoother used by smoothed GRV proxy limiter policies. It tracks a total and a lagging estimate, then derives smoothed totals and rates.

## Important APIs, Types, And Functions
`Smoother(folding_time)` initializes smoothing with a time constant. `reset(value)` resets time, total, and estimate. `set_total(time, total)` converts an absolute total to a delta. `add_delta(time, delta)` first advances the estimate, then increments total. `smooth_total(time)` updates and returns the estimate. `smooth_rate(time)` updates and returns `(total - estimate) / folding_time`. `update(time)` advances the estimate by `1 - exp(-elapsed / folding_time)` when elapsed is positive.

## Control Flow
The class is call-driven. Every public read/write method funnels through `update`, which is a no-op for non-positive elapsed time and an exponential interpolation toward `total` for positive elapsed time.

## State And Persistence Behavior
The object stores `folding_time`, `time`, `total`, and `estimate` in memory. There is no persistence or external state.

## Dependencies And Integration Points
It depends on Python's `math.exp`. `proxy_model.SmoothingLimiter` uses two instances to smooth rate limits and released request counts, and `SmoothingBudgetLimiter` records smoothed values into results.

## Risks And Edge Cases
`folding_time` is not validated; zero causes division by zero and negative values invert the smoothing behavior. Non-monotonic time is ignored because negative elapsed does not update, which can leave `self.time` ahead of future calculations. Large elapsed values effectively snap the estimate to total.

## Test Signals
Tests should assert reset behavior, monotonic convergence, rate calculation after deltas, no update on same/earlier time, and error/guard behavior for zero folding time if validation is added.
