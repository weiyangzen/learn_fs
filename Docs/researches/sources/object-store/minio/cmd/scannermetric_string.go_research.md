# sources/object-store/minio/cmd/scannermetric_string.go

Purpose: This is generated `stringer` output for the `scannerMetric` enum defined elsewhere in the data scanner code. It provides stable, allocation-light names for scanner metrics used in tracing, logging, metrics labels, or diagnostics.

Important APIs and types: The only exported behavior here is `(scannerMetric).String() string`. The generated `_()` function contains compile-time array-index checks tying this file to exact enum ordinal values from `scannerMetricReadMetadata` through `scannerMetricLast`. `_scannerMetric_name` stores concatenated names, and `_scannerMetric_index` stores byte offsets into that string.

Control flow: `String` bounds-checks the metric value against the index table. Known values return a slice of `_scannerMetric_name`; unknown values return a fallback of the form `scannerMetric(<n>)` using `strconv.FormatInt`.

State and persistence behavior: There is no runtime mutable state or persistence. The important state is generated source consistency: if enum order changes without regenerating this file, compile-time checks should fail.

Dependencies and integration points: It depends on the `scannerMetric` constants in data scanner code and on Go's `strconv`. Consumers use the string form when scanner phases are reported or traced, so name stability matters for observability.

Risks: Manual edits or stale generation can mislabel scanner phases. The index table uses `uint8`, which is sufficient for the current concatenated string length but would need regeneration if names or count grow beyond its assumptions. The file should not be hand-maintained.

Test signals: There are no direct tests in this subset. Compiler failures from the generated guard are the main safety signal; observability tests elsewhere could assert selected metric names.
