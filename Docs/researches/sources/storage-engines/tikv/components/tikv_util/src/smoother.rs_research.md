# sources/storage-engines/tikv/components/tikv_util/src/smoother.rs

## Purpose
Implements a generic fixed-capacity sliding-window smoother for recent numeric observations, including average, max, 90th percentile, and coarse trend detection.

## Important APIs, Types, and Functions
- `Trend::{Increasing,Decreasing,NoTrend}` reports trend direction.
- `Smoother<T, CAP, STALE_DUR, MIN_TIME_SPAN>` stores a `VecDeque<(T, Instant)>` and running `total`.
- `observe` and `observe_with_time` add records, enforce capacity, and remove stale records while keeping at least two records.
- Read methods include `get_count`, `get_recent`, `get_avg`, `get_max`, `get_percentile_90`, and `trend`.

## Control Flow
Adding a record evicts the oldest when capacity is full, updates the running total, pushes the new timestamped record, then removes stale front records beyond `STALE_DUR` as long as at least two records remain. Trend detection returns no trend for too few or stale records; otherwise it compares left/right averages by time split when `MIN_TIME_SPAN > 0`, or by count split when zero, using a tolerance of 2.0.

## State and Persistence Behavior
The smoother stores only in-memory recent observations and a running sum. It can be cloned when `T: Clone`, preserving the current window snapshot.

## Dependencies and Integration Points
Depends on `num_traits::{AsPrimitive,FromPrimitive}` and crate `time::Instant`. It is a reusable helper for flow/stat smoothing in higher-level components.

## Risks
`partial_cmp(...).unwrap()` will panic for non-orderable values such as `NaN` floats. `get_percentile_90` sorts a temporary vector and mutably borrows `self` despite not modifying fields. Running total depends on arithmetic traits and can overflow for integer `T` in release builds if callers choose unsuitable types/capacities.

## Test Signals
Tests cover average/recent/max/percentile behavior, capacity count, count-based trends, time-span-gated trends, increasing/decreasing/no-trend cases, and stale-record no-trend behavior.
