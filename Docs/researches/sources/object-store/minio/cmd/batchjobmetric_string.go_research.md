# sources/object-store/minio/cmd/batchjobmetric_string.go

This generated `stringer` file provides `String()` for the `batchJobMetric` enum defined elsewhere, with a trim prefix of `batchJobMetric`. It maps metric constants to compact human-readable labels used in metric/logging paths.

The compile-time guard in `_()` indexes an array by `batchJobMetricReplication-0`, `batchJobMetricKeyRotation-1`, and `batchJobMetricExpire-2`. If enum values are reordered or changed without regenerating this file, compilation fails with an invalid array index. `_batchJobMetric_name` stores the concatenated labels `ReplicationKeyRotationExpire`, and `_batchJobMetric_index` slices that string into the three names.

`func (i batchJobMetric) String() string` returns the generated label for valid values and falls back to `batchJobMetric(<number>)` for out-of-range values via `strconv.FormatInt`. There is no persistent state, but the string output is an integration point for observability, metric naming, trace reporting, and diagnostics around replication, key rotation, and expiration batch jobs.

Dependencies are minimal: only `strconv` and the enum constants. Risks are stale generated code when adding new metric types and downstream dashboards depending on exact string values. There is no dedicated test in this subset; compile-time checks are the main safety mechanism.
