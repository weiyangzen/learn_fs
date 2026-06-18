<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/skewed_latest_test.go -->
# sources/storage-engines/pebble/internal/randvar/skewed_latest_test.go

Purpose: tests and optional visualization helpers for `SkewedLatest`.

Important APIs/functions: `dumpSamples`, `TestSkewedLatest`, and `TestSkewedLatestMax`.

Control flow and state: `dumpSamples` sorts samples and prints a rough histogram using block characters during verbose runs. `TestSkewedLatest` constructs a generator over `[0,99]`, draws 10,000 samples, and optionally dumps the distribution. `TestSkewedLatestMax` verifies initial `Max`, increments by 50, verifies new max, and draws 1,000 samples asserting each lies within `[min, Max()]`.

Dependencies and integration: uses `testify/require` and `NewRand`. The tests give range and smoke coverage but do not assert skew shape statistically. Risks not covered include invalid constructor args, concurrent `IncMax` and reads, deterministic reproducibility, and nil RNG behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/skewed_latest_test.go -->
