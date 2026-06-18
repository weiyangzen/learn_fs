# sources/object-store/minio/cmd/metrics-v3-ilm.go

Purpose: Exposes v3 ILM expiration, transition, and lifecycle scanner counters.

Important APIs/types/functions: Defines metrics for pending expiry tasks, active/pending transition tasks, missed immediate transition tasks, and versions scanned. `loadILMMetrics` populates these values.

Control flow: The loader checks `globalExpiryState` before setting pending expiry tasks, checks `globalTransitionState` before setting transition gauges/counter, and always sets lifecycle versions scanned from `globalScannerMetrics.lifetime(scannerMetricILM)`.

State and persistence behavior: Stateless over global lifecycle worker state and scanner counters. Metrics are process runtime values.

Dependencies and integration points: Depends on global expiry/transition state and scanner metrics. It separates ILM telemetry from the larger v2 scanner/ILM block.

Risks: When expiry or transition state is nil, corresponding metrics are omitted rather than emitted as zero. Consumers must handle absent series during startup or disabled subsystems.

Test signals: No direct tests in this subset.
