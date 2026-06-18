<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/server.rs -->
# sources/object-store/rustfs/crates/obs/examples/server.rs

## Purpose
Demonstrates initializing observability and emitting trace/log/metric data from a Tokio program. It simulates a service run and a `put_object` operation with spans and histogram records.

## Important APIs, Types, and Functions
`main` calls `rustfs_obs::init_obs` with a local OTLP endpoint, creates a tracing span, logs lifecycle messages, and calls `run`. `run` and `put_object` are annotated with `#[instrument(fields(bucket, object, user))]`. Both use `opentelemetry::global::meter("rustfs")` and an `s3_request_duration_seconds` histogram.

## Control Flow
The async main initializes telemetry, enters a top-level span, sleeps briefly, invokes `run`, then exits. `run` records a duration metric and calls `put_object`, which records another duration metric and sleeps to simulate work.

## State and Persistence
State is local and transient. The `_guard` returned by `init_obs` is kept alive for the example duration so telemetry providers can flush on drop. Exported telemetry may persist in the configured collector.

## Dependencies and Integration
Uses `rustfs_obs`, OpenTelemetry global meter, Tokio time, and tracing macros. It integrates with whatever exporters `init_obs` configures.

## Risks
`init_obs` returns a `Result`, but the example stores it directly without handling failure; if initialization fails, `_guard` is an error value and telemetry may not be active. Repeated histogram construction inside functions is acceptable for demos but not ideal for hot paths.

## Test Signals
This is an example rather than a unit test. It can be run manually against a collector at `http://localhost:4318` to verify log/span/metric export.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/server.rs -->
