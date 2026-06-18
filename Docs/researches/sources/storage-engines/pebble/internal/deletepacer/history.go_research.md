# sources/storage-engines/pebble/internal/deletepacer/history.go

## Purpose
`history.go` implements a fixed-size rolling history used by the delete pacer to track recent byte totals at coarse time granularity. It is optimized for cheap additions and approximate-window sums over a configured timeframe.

## Important APIs, Types, And Functions
`history` stores `epochDuration`, `startTime`, `currEpoch`, a 100-entry `val` ring, and a cached `sum`. `historyEpochs` is fixed at 100. `Init(now, timeframe)` configures the epoch size as `timeframe / 100`. `Add(now, val)` advances to the current epoch and increments that bucket. `Sum(now)` advances and returns the cached rolling sum. Internal helpers `epoch` and `advance` translate monotonic time to epoch indexes and discard expired buckets.

## Control Flow
Every public operation calls `advance`. `advance` increments `currEpoch` until it catches up with the epoch for `now`, subtracting and zeroing the ring bucket that becomes oldest on each step. `Add` then writes into `val[currEpoch % historyEpochs]`; `Sum` only returns `sum`.

## State And Persistence Behavior
The state is process-local and approximate. It retains at most 100 epochs and loses precision by rounding time down to epoch boundaries. It relies on `crtime.Mono`, so it is monotonic-time safe and not wall-clock persistent.

## Dependencies And Integration Points
The delete pacer uses it for recent deletion byte rate estimation, especially `RecentRateWindow`. It depends on `crtime` and `invariants.SafeSub`, which clamps underflow in production and panics in invariant builds.

## Risks And Edge Cases
If `timeframe < 100ns`, `epochDuration` can be zero and division would panic; callers are expected to use meaningful windows. Very large jumps advance one epoch at a time, so pathological time jumps cost O(number of elapsed epochs). Approximation is bounded by the 1 percent epoch granularity.

## Test Signals
Coverage is indirect through deletepacer datadriven pacing behavior and rate/backlog tests. Useful direct tests would verify bucket expiration, large time jumps, and the invariant underflow guard.
