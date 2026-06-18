# sources/test-tools/syzkaller/tools/syz-testbed/stats.go

## Purpose
This file defines result models and table/bench generation for `syz-testbed` manager and repro experiments.

## Important APIs, types, and functions
- Data types: `BugInfo`, `RunResult`, `SyzManagerResult`, `SyzReproResult`, `StatRecord`, `RunResultGroup`, and `StatView`.
- Collection helpers: `collectBugs`, `readBenches`, and `groupSamples`.
- Bug summaries/tables: `summarizeBugs`, `GenerateBugTable`, `GenerateBugCountsTable`.
- Type filters: `SyzManagerResults`, `SyzReproResults`.
- Stat alignment/averaging: `AvgStatRecords`, `minResultLength`, `groupNthRecord`, `groupLastRecord`, `StatsTable`, `AlignedStatsTable`, `InstanceStatsTable`.
- Repro tables: `GenerateReproSuccessTable`, `GenerateCReproSuccessTable`, `GenerateReproDurationTable`, `GenerateReproAttemptsTable`.
- Persistence helpers: `SaveAvgBenchFile`, `SaveAvgBenches`, `IsEmpty`.

## Control flow
Manager stats collect crash titles/log paths and JSON bench records. Group-level methods filter result unions by concrete result type. For aligned stats, each group contributes the latest sample at or above the minimum common value of an alignment field, usually uptime. Repro tables aggregate by input title, counting success ratios, C repro ratios, durations, or every attempt row.

## State and persistence behavior
Reads crash stores and bench files. Writes averaged bench files under caller-provided directories. All summary tables are in-memory until saved by target or HTTP code.

## Dependencies and integration points
Uses `pkg/manager.ReadCrashStore` for bug lists and `pkg/stat/sample` for median, outlier removal, and statistical samples. Tables are consumed by `targets.go`, `html.go`, and CSV persistence.

## Risks and edge cases
`readBenches` ignores JSON decode errors inside the stream, potentially hiding corrupt records. `minResultLength` assumes there is at least one manager result when `len(group.Results) > 0`; mixed or repro-only groups can panic if used with manager stats. `GenerateBugCountsTable` divides by `len(group.Results)` for found bugs, but empty groups do not set cells. The duration table comment incorrectly mentions C repro share.

## Test signals
No direct tests in this file. It has indirect coverage from table tests only. High-value tests would cover malformed bench JSON, mixed result groups, stat alignment missing fields, repro aggregation, and bench downsampling.
