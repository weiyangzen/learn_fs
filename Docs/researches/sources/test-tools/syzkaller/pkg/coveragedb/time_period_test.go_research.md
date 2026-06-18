# sources/test-tools/syzkaller/pkg/coveragedb/time_period_test.go

Purpose: validates date-period calculations and merge scheduling logic for coverage aggregation.

Important APIs/types/functions: `TestDayPeriodOps`, `TestMonthPeriodOps`, `TestQuarterPeriodOps`, `TestPeriodsToMerge`, helper `makeTimePeriod`, `TestAtMostNLatestPeriods`, and `TestMakeTimePeriod`.

Control flow: tests check last-period date, period validity, period day counts, and generated period sequences for day/month/quarter including leap-year February. `TestPeriodsToMerge` compares daily source rows against already-merged day/month/quarter periods to identify missing or stale merges. Latest-period and invalid date behavior are also asserted.

State and persistence: no external state.

Dependencies and integration: uses `civil.Date` and testify assertions. Tests directly cover `time_period.go`.

Risks: tests use helper-created `TimePeriod` values without `Type` for some merge expectations, matching current `PeriodsToMerge` behavior. They do not test `MinMaxDays` or unknown period errors.

Test signals: strong date math coverage, especially for aggregation correctness around month/quarter boundaries.
