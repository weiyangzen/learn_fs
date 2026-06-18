# sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/historgram.xml

## Purpose
This Splunk dashboard, despite the misspelled filename, displays FoundationDB CommitProxy and TLog latency histograms plus commit latency summary charts. It gives operators bucketed views of transaction pipeline stages.

## Important APIs, Types, And Functions
The form label is `FoundationDB - Histograms` and uses tokens `Index`, `LogGroup`, and `TimeSpan`. Panels chart `CommitLatencyMetrics` summary fields and `Histogram` events for CommitProxy operations `CommitBatchQueuing`, `GetCommitVersion`, `Resolution`, `PostResolutionQueuing`, `ProcessingMutation`, `ReplyCommit`, `TlogLogging`, and `ToTlog_*`, plus TLog operations `QueueWait`, `TimeUntilDurable`, and `commit`.

## Control Flow
The fieldset defaults `Index` to `iffdb` and `TimeSpan` to the last hour, with `autoRun=false`. Each histogram query filters by tokens, event type, group, and operation, runs `foreach LessThan*`, and charts `avg(LessThan*)` over time. Histogram panels are stacked column charts; commit latency summary is a line chart over max/mean/P95/P99/P99.9.

## State And Persistence Behavior
The file is static dashboard configuration and writes no state. Runtime state is limited to Splunk tokens and chart rendering.

## Dependencies And Integration Points
It depends on Splunk Simple XML and FDB trace events that emit `Histogram` fields named `LessThan*`. It integrates with the same observability dashboard set as details and performance overview.

## Risks And Edge Cases
The filename typo `historgram.xml` can break automation expecting `histogram.xml`. The `foreach LessThan* [eval newfield=<<FIELD>>]` command appears to create a generic `newfield` without using it, so it may be redundant or misleading. Averaging cumulative histogram buckets across machines can obscure per-machine outliers. `autoRun=false` means users must submit or change inputs before searches run.

## Test Signals
Tests should import the dashboard in Splunk, verify searches compile, confirm histogram fields render as stacked columns with sample data, check empty data handling, and decide whether the filename typo is intentionally referenced elsewhere.
