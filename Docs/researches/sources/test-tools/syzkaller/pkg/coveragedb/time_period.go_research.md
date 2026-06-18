# sources/test-tools/syzkaller/pkg/coveragedb/time_period.go

Purpose: models daily, monthly, and quarterly coverage aggregation periods and computes which periods require merging.

Important APIs/types/functions: `TimePeriod`, `DatesFromTo`, `MakeTimePeriod`, constants `DayPeriod`, `MonthPeriod`, `QuarterPeriod`, `AllPeriods`, `MinMaxDays`, `PeriodOps`, `GenNPeriodsTill`, period op structs, `PeriodsToMerge`, and `AtMostNLatestPeriods`.

Control flow: period ops normalize arbitrary dates to the last day of the containing day/month/quarter and compute period length. `MakeTimePeriod` validates that a target date points to the period end. `GenNPeriodsTill` walks backward by period lengths and returns chronological order. `PeriodsToMerge` aggregates source daily rows by target period end, removes periods already merged with matching row counts, and returns missing/stale periods newest first.

State and persistence: pure date/value functions; no persistence.

Dependencies and integration: uses `civil.Date` for date-only values. `coveragedb` queries and `covermerger.InitNsRecords` use these ranges/durations.

Risks: `PeriodsToMerge` constructs returned `TimePeriod` values without setting `Type`, unlike `MakeTimePeriod`/`GenNPeriodsTill`. Quarter day calculations manually decrement months and rely on `civil.Date` month behavior. Leap years are covered by tests.

Test signals: `time_period_test.go` covers day/month/quarter ops, merge-period detection, latest-period limiting, and invalid quarter end dates.
