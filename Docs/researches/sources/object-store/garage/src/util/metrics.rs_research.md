<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/metrics.rs -->
# sources/object-store/garage/src/util/metrics.rs

## Purpose
Metric utility helpers for timing futures and generating trace identifiers.

## Important APIs, types, and functions
`RecordDuration` extension trait offers `record_duration` and `bound_record_duration` for futures. `gen_trace_id` creates an OpenTelemetry `TraceId` from random bytes.

## Control flow
The wrapper records `Instant::now()` before awaiting a future, then records elapsed seconds into an OpenTelemetry value recorder with provided attributes after completion.

## State and persistence behavior
No persistent state. Runtime telemetry state is emitted through OpenTelemetry meters/traces.

## Dependencies and integration points
Used by table and web request paths to record latency. Depends on futures, OpenTelemetry metrics/trace types, and `rand`.

## Risks and test signals
Timing wrappers must preserve future output and lifetime behavior. Tests can wrap successful and failing futures and assert recorder invocation through a test meter provider.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/metrics.rs -->
