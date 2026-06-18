# sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/details.xml

## Purpose
This Splunk Simple XML dashboard provides detailed operational views for a FoundationDB log group. It focuses on storage queues, process/network load, connection failures, roles, slow tasks, errors, recoveries, disk space, data movement, and failed clients with filterable index/log group/time/role/host/machine inputs.

## Important APIs, Types, And Functions
The dashboard is a `<form version="1.1" theme="dark">` named `FoundationDB - Details`. Inputs define tokens `Index`, `LogGroup`, `TimeRange`, `Span`, `Roles`, `Host`, and `Machine`. Panels use Splunk searches against FDB trace event types including `StorageMetrics`, `ProcessMetrics`, `NetworkMetrics`, `TLogMetrics`, `ConnectionTimeout`, `ConnectionTimedOut`, `SpringCleaningMetrics`, `SlowTask`, `MasterRecoveryState`, `ProgramStart`, `FailureDetectionStatus`, `MovingData`, and `WaitFailureClient`.

## Control Flow
Splunk fills tokens from the fieldset, then each row/panel runs its `<search>` over `$TimeRange.earliest$` and `$TimeRange.latest$`. Most charts use `timechart $Span$ ... by Machine/Roles`; tables use `stats`, `sort`, and `table`. Several panels derive metrics with `rex`, `eval`, `streamstats`, `join`, `makemv`, and `mvexpand`.

## State And Persistence Behavior
The XML is declarative dashboard configuration. It stores no runtime state beyond Splunk dashboard tokens and does not mutate FDB or Splunk indexes.

## Dependencies And Integration Points
It depends on Splunk Simple XML 1.1, FDB trace logs indexed with fields such as `Type`, `LogGroup`, `Machine`, `host`, `Roles`, and `TrackLatestType`, and a convention where rolled/original metric events are searchable. It integrates with operators' Splunk app import/deployment process.

## Risks And Edge Cases
The broad token substitution can create expensive searches, especially joins and high-cardinality `timechart by Machine`. Filters such as `host=$Host$` assume token defaults like `*` are present and safe. Some panels explicitly ignore filters, which may surprise users. The long recovery query is complex and fragile against field name changes. The file has no explicit tests or dashboard validation metadata.

## Test Signals
Validation should load the XML in Splunk, confirm all tokens resolve, and run representative searches on sample FDB trace data. Search tests should cover default wildcard filters, role filtering, machine filtering, empty result sets, and performance of connection timeout/recovery panels over large time ranges.
