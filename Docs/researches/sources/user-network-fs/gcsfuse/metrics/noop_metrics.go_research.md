## sources/user-network-fs/gcsfuse/metrics/noop_metrics.go

Purpose: Auto-generated no-op implementation of `MetricHandle`.

Important APIs/types/functions: unexported `noopMetrics` implements every `MetricHandle` method with empty bodies; `NewNoopMetrics()` returns it as a `MetricHandle`.

Control flow: all metric calls are accepted and discarded.

State and persistence behavior: no state or metric emission.

Dependencies and integration points: used when metrics are disabled and in tests that need a non-nil metric handle, such as retry monitoring tests.

Risks: must be regenerated whenever `MetricHandle` changes. Because it silently drops metrics, accidental use in production instrumentation paths can hide telemetry.

Test signals: compile-time interface conformance is the main signal; dependent tests use it as a safe stub.
