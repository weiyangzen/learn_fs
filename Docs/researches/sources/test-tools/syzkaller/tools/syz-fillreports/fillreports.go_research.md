# sources/test-tools/syzkaller/tools/syz-fillreports/fillreports.go

Purpose: `syz-fillreports` backfills missing report elements on dashboard bugs, currently guilty file paths extracted from crash reports.

Important APIs and flow: `main` creates a `dashapi.Dashboard`, fetches `BugList`, loads bug reports concurrently with `loadBugReports`, and calls `processReport`. `processReport` skips reports that already have guilty files, are not open/fixed, or lack OS/arch; creates a minimal `mgrconfig.Config` with target info; builds a `report.Reporter`; extracts a guilty file with `ReportToGuiltyFile`; and uploads it through `dash.UpdateReport`.

State and persistence: dashboard is the persistent state. Local state is a work item channel and worker goroutines. No local files are written.

Dependencies and integration: uses dashboard API credentials, syzkaller report parsing, target metadata, and manager config-derived reporter construction.

Risks: `log.Fatalf` on reporter creation stops the whole run for one bad OS/arch. It only handles the first extracted guilty file. Load failures are logged and skipped; update failures are logged but do not abort. Concurrency is fixed at 8.

Test signals: no direct test. Report parser tests and dashboard API mocks would be needed for coverage.
