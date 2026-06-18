## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Smoother.h

Purpose: Provides reusable exponential and Holt linear smoothing helpers for metrics and queue estimates.

Important APIs/types/functions: `SmootherImpl<T>` implements basic exponential smoothing with `reset()`, `setTotal()`, `addDelta()`, `smoothTotal()`, `smoothRate()`, and `getTotal()`. `Smoother` uses `now()`, while `TimerSmoother` uses `timer()`. `HoltLinearSmootherImpl<T>` implements double exponential smoothing with trend estimation and the same total/rate accessors. `HoltLinearSmoother` and `HoltLinearTimerSmoother` provide clock-specific wrappers.

Control flow: Basic smoothing updates the estimate lazily when callers add deltas or read smoothed values, using elapsed time and e-folding time. Holt smoothing updates estimate and rate snapshots when deltas arrive, then predicts total/rate based on elapsed time and trend.

State and persistence behavior: State is in-memory numeric totals, estimates, rates, and timestamps. No serialization.

Dependencies and integration points: Depends on Flow time functions and `<cmath>`. `QueueModel` uses `Smoother` for smoothed outstanding request counts; metrics code can use timer variants.

Risks: Time values are expected nondecreasing; negative elapsed time would distort estimates. Very small e-folding times can create unstable or near-step behavior. `HoltLinearTimerSmoother` members are private by default in the header, which may limit construction/use unless intentional.

Test signals: Deterministic fake-clock tests for add/set/read, zero elapsed behavior, rate calculation, reset, trend-following behavior, and nondecreasing-time assumptions.
