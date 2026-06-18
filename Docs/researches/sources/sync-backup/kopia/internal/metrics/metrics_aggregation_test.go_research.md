# sources/sync-backup/kopia/internal/metrics/metrics_aggregation_test.go

Purpose: verifies snapshot aggregation for counters, size distributions, and duration distributions.

Important APIs/types/functions: `metrics.AggregateSnapshots`, `metrics.Snapshot`, `DistributionState`, and helper `toJSON`.

Control flow: the test constructs four snapshots with overlapping and distinct counters plus matching distribution states. It aggregates them, asserts counter sums, and compares marshaled JSON for merged distributions including min, max, sum, count, and bucket counts.

State/persistence behavior: no persistent state. JSON comparisons mirror how distribution states appear in serialized output.

Dependencies/integration: uses `time.Duration` distribution states and `testify/require`.

Risks/test signals: exact JSON comparisons catch field-level regressions but do not verify start/end time handling. Bucket compatibility mismatch is not tested.
