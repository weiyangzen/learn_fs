## sources/user-network-fs/gcsfuse/metrics/metric_handle.go

Purpose: Auto-generated metrics API defining attribute types/constants and the `MetricHandle` interface.

Important APIs/types/functions: attribute string types for entry status, filesystem errors/ops, GCS methods, I/O method, lookup detail, open mode, read type, fallback reason, request type, retry category, and write fallback reason. `MetricHandle` declares methods for all generated counters and histograms.

Control flow: interface-only generated file; concrete implementations record metrics, while noop implementation discards them.

State and persistence behavior: no state. The generated constants are compile-time labels used by metric emitters.

Dependencies and integration points: generated from `metrics.yaml` and used throughout gcsfuse for OpenTelemetry instrumentation and tests.

Risks: manual edits will be overwritten. Schema changes must keep `metrics.yaml`, generated handle, noop implementation, and otel implementation synchronized.

Test signals: metrics implementation tests and helpers validate concrete emission; this file itself is compile-time checked by implementers such as `noopMetrics`.
