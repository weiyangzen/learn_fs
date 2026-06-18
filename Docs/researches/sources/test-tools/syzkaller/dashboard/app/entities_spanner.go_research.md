# sources/test-tools/syzkaller/dashboard/app/entities_spanner.go

Purpose: Spanner-backed coverage history aggregation for dashboard coverage views.

Important APIs/types/functions: `CoverageHistory` and `MergedCoverage(ctx, client, ns, periodType)`.

Control flow: `MergedCoverage` resolves valid duration bounds and period operations from `coveragedb`, runs a parameterized Spanner SQL query joining `merge_history` and `files`, iterates rows, validates `coveragedb.TimePeriod` values, records instrumented/covered totals by target date, and rejects duplicate valid periods.

State/persistence: read-only against Spanner; returns in-memory maps keyed by `civil.Date.String()` plus a set of valid periods.

Dependencies/integration: depends on `spannerclient.SpannerClient`, `cloud.google.com/go/spanner`, `civil.Date`, `coveragedb`, and `iterator.Done`; integrates with coverage UI/reporting.

Risks/test signals: strict duplicate-period errors can surface database-shape issues; per-date maps may be limiting if future period types allow multiple valid durations for one date. No direct subset test; coverage mock tests elsewhere should validate row parsing and filtering.
