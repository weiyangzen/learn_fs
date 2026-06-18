<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/split_test.go -->
# sources/storage-engines/pebble/internal/mkbench/split_test.go

Purpose: table-driven tests for `findOptimalSplit`.

Important APIs/functions: `TestFindOptimalSplit` defines pass/fail arrays and expected split values, using `require.Equal`.

Control flow and state: cases cover no data, one side missing, a trivial one-pass/one-fail split, the example from the function comment, and a large empirical data set from an actual run. Each test invokes `findOptimalSplit` and checks the exact threshold.

Dependencies and integration: uses `testing` and `testify/require`. The empirical case gives realistic noisy pass/fail overlap coverage for the write-throughput parser. Risks not covered include negative inputs, pass/fail distributions with reversed ordering, plateau behavior across unusual ranges, and sensitivity to `increment` changes beyond expected fixture updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/split_test.go -->
