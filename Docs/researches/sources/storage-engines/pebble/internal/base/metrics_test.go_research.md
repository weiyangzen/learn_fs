# sources/storage-engines/pebble/internal/base/metrics_test.go

Purpose: Tests throughput and gauge metric accumulation helpers in `base`.

APIs and types: Exercises `ThroughputMetric.Merge`, `Subtract`, `Rate`, `PeakRate`, and `GaugeSampleMetric.AddSample`, `Merge`, `Subtract`, and `Mean`.

Control flow and state: Constructs representative byte/time metrics, merges duplicate values, subtracts one metric from another, and checks expected rates. Gauge tests add samples, merge gauges, subtract prior samples, and inspect internal sum/count.

Persistence and dependencies: No persistence. Uses test assertions to guard text output.

Integration points: Protects helper arithmetic used by DB metrics and background work accounting.

Risks: Tests cover simple positive cases and one subtraction case; they do not cover zero-duration nonzero-byte edge cases.

Test signals: Good local coverage for arithmetic and rate formulas.
