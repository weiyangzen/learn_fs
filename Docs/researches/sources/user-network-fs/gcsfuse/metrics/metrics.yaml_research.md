## sources/user-network-fs/gcsfuse/metrics/metrics.yaml

Purpose: Source schema for generated metrics code.

Important APIs/types/functions: YAML entries define metric names, descriptions, units, types, histogram boundaries, attributes, and allowed values. Anchors share microsecond, millisecond, byte, read-type, and GCS-method lists.

Control flow: consumed by `tools/metrics-gen` from the `main.go` go-generate directive to produce `metric_handle.go`, `noop_metrics.go`, and concrete OpenTelemetry code.

State and persistence behavior: static configuration; edits regenerate code and affect telemetry contracts.

Dependencies and integration points: defines all observable gcsfuse metric names including buffered read fallback/latency, file cache reads, fs ops/errors/latency, streaming write fallback, GCS read/download/request/retry metrics, metadata cache reads, block sizes, and test up-down counters.

Risks: changing names, units, boundaries, or attribute values is a telemetry compatibility change. YAML anchors reduce duplication but can hide broad impact from local edits.

Test signals: generated code compilation and OpenTelemetry metric tests validate schema consistency.
