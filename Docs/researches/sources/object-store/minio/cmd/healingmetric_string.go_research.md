<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/healingmetric_string.go -->
# sources/object-store/minio/cmd/healingmetric_string.go

## Purpose
Generated `stringer` output for the `healingMetric` enum from `erasure-healing.go`. It maps metric constants to stable names for logging/metrics display.

## Important APIs, types, and functions
- Compile-time checks assert `healingMetricBucket`, `healingMetricObject`, and `healingMetricCheckAbandonedParts` numeric values.
- `_healingMetric_name` and `_healingMetric_index` encode `Bucket`, `Object`, and `CheckAbandonedParts`.
- `(healingMetric).String()` returns the generated name or `healingMetric(<n>)` for out-of-range high values.

## Control flow
The string method checks the upper bound and slices the generated compact name table. Unlike some stringer outputs, negative enum values are not explicitly rejected before indexing, so callers should not pass negative values.

## State and persistence behavior
No state or persistence. It is generated code and should be regenerated when enum constants change.

## Dependencies and integration points
Used by erasure healing metrics/logging code. Depends only on `strconv` and enum constants defined elsewhere.

## Risks and edge cases
Manual edits or enum changes without regeneration can break names or compile-time checks. Negative enum values can index before bounds if ever constructed.

## Test signals
Build success verifies generated constant checks. Runtime metric tests elsewhere should catch unexpected string names.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/healingmetric_string.go -->
