<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/split.go -->
# sources/storage-engines/pebble/internal/mkbench/split.go

Purpose: computes an ops/sec threshold separating successful and failed write-throughput measurements with minimal misclassification.

Important APIs/functions: constant `increment = 50` and `findOptimalSplit(pass, fail []int) int`.

Control flow and state: the function rejects missing pass or fail data with `-1`, copies and sorts inputs, scans thresholds from minimum pass to maximum fail in 50 ops/sec increments, updates counts of misclassified passes and fails, and records `(threshold, error)` pairs. It sorts candidates by error and threshold, then averages the lowest and highest threshold within the best-error plateau.

Persistence and integration: pure computation with no persistent state. It is used by `rawWriteRun.opsPerSecSplit` in write benchmark cooking. Risks include assumptions that pass values should be below the split and fail values above it, scan bounds using first pass and last fail after sorting, coarse 50 ops/sec resolution, and possible odd behavior if all fails are below all passes. Unit tests cover empty, trivial, documented, and empirical cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/split.go -->
