# sources/sync-backup/kopia/internal/metrics/metrics_registry_test.go

Purpose: validates nil-safe registry logging/closing and the log output produced for counters, throughput, duration distributions, and size distributions.

Important APIs/types/functions: `metrics.NewRegistry`, `Registry.CounterInt64`, `Throughput`, `DurationDistribution`, `SizeDistribution`, `Registry.Log`, and `Registry.Close`.

Control flow: nil test calls `Log` and `Close` on a nil registry. Non-nil test writes log output to a buffer, records several metrics, logs them, closes the registry, sorts lines, and compares exact structured log output.

State/persistence behavior: uses in-memory registry state and buffer-backed logging. The test exercises release tracking through `Close` but does not inspect it directly.

Dependencies/integration: integrates metrics with repository logging's writer adapter and `testify/require`.

Risks/test signals: exact log-line assertions catch output format changes. The test uses single-label-free metrics and does not cover snapshot time metadata.
