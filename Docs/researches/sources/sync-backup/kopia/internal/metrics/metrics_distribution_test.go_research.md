# sources/sync-backup/kopia/internal/metrics/metrics_distribution_test.go

Purpose: verifies binary-search bucket selection over distribution thresholds.

Important APIs/types/functions: `bucketForThresholds`, `IOLatencyThresholds.values`, and `math.MaxInt64`.

Control flow: the test checks a value below the first threshold maps to bucket zero. For every threshold it verifies `threshold-1` and exact threshold map to the current bucket, while `threshold+1` maps to the next bucket. A huge value maps to the overflow bucket.

State/persistence behavior: no mutable or persistent state. It validates pure threshold logic used by distributions.

Dependencies/integration: package-internal access to threshold values and helper function. Uses `testify/assert`.

Risks/test signals: focused on integer-like duration thresholds; it does not test floating-point threshold behavior even though the generic helper permits floats.
