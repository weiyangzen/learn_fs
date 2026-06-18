# sources/storage-engines/rocksdb/trace_replay/trace_record_result.cc

## Purpose

Implements result objects produced by trace execution: status-only, single-value, multivalue, and iterator results with execution timing and trace type metadata.

## Important APIs, Control Flow, And Dependencies

`TraceRecordResult` stores `TraceType`. `TraceExecutionResult` stores start and end timestamps and asserts nondecreasing order. `StatusOnlyTraceExecutionResult`, `SingleValueTraceExecutionResult`, `MultiValuesTraceExecutionResult`, and `IteratorTraceExecutionResult` each own the relevant status/value fields and implement `Accept(Handler*)` for visitor-style result handling. Iterator results store validity plus pinned key/value slices.

## State, Persistence, Integration, Risks, And Test Signals

These are in-memory replay result carriers; they do not persist data themselves. They integrate with `TraceExecutionHandler` and any consumer implementing `TraceRecordResult::Handler`. Destructors clear owned strings/vectors/pinned slices. Risks include value copying/moving costs for large replay results, assert-only timestamp validation, and requiring callers to inspect embedded statuses because replay may return OK while a traced Get/MultiGet item was `NotFound`. Coverage is indirect via replay users and tests.
