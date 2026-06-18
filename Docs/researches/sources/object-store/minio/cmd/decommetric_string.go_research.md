<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/decommetric_string.go -->
## sources/object-store/minio/cmd/decommetric_string.go

Purpose: This generated `stringer` file provides the `String()` method for the `decomMetric` enum defined in decommissioning code. It maps metric constants to stable names used in logs, metrics, or diagnostics.

Important APIs and functions: The compile-time guard function `_()` indexes a one-element array with expected enum offsets to fail compilation if `decomMetricDecommissionBucket`, `decomMetricDecommissionObject`, or `decomMetricDecommissionRemoveObject` change values without regeneration. `_decomMetric_name` stores concatenated names, `_decomMetric_index` stores offsets, and `(decomMetric).String()` returns the name for known enum values or `decomMetric(<n>)` for out-of-range values.

Control flow: `String()` checks whether the enum is greater than or equal to the last valid index; if so it formats an unknown numeric value with `strconv.FormatInt`. Otherwise it slices the concatenated name string using the generated index table.

State and persistence behavior: No mutable state or persistence exists. The generated strings may become externally visible through logs or metrics, so names are a lightweight compatibility surface.

Dependencies and integration points: It imports only `strconv` and integrates with `decomMetric` constants in `erasure-server-pool-decom.go`. It should be regenerated with `stringer -type=decomMetric -trimprefix=decomMetric erasure-server-pool-decom.go` when enum constants change.

Risks: Manual edits can be overwritten by regeneration. Adding, removing, or reordering enum constants without regenerating causes either a compile failure from the guard or incorrect string output if a change bypasses the guard pattern.

Test signals: No direct tests are present. The compile-time guard is the primary protection.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/decommetric_string.go -->
