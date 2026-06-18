# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_timeres_test.go

Purpose: verifies Kopia metric time-bucket resolution functions for day, week, quarter, and year boundaries.

Important APIs/types/functions: `TestTimeResolutions`, helper constructors `dayOf`/`monthOf`, and exported metric functions `TimeResolutionByDay`, `TimeResolutionByWeekStartingSunday`, `TimeResolutionByWeekStartingMonday`, `TimeResolutionByQuarter`, and `TimeResolutionByYear`.

Control flow: table-driven cases compute expected start and exclusive end; each case checks exact input, period start, last moment before period end, and midpoint all resolve to the same bucket.

State and persistence behavior: no persistent state; test is deterministic around fixed UTC dates.

Dependencies and integration points: uses `testify/require` and the public `internal/metrics` package, acting as regression coverage for time-series aggregation.

Risks and test signals: protects off-by-one and week-start regressions. It does not cover DST/local time zones, leap years, or all quarter boundaries.
