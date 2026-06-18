<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/welford_test.go -->
# sources/storage-engines/pebble/internal/metricsutil/welford_test.go

Purpose: unit tests for unweighted and weighted Welford statistics.

Important APIs/functions: `almostEqual`, `TestWelfordBasic`, and `TestWeightedWelford`. The tests assert empty, single-value, constant, simple 1..5, and mixed repeated distributions.

Control flow and state: table-driven tests instantiate zero-value accumulators, feed input values, and compare count, mean, and sample variance with a small epsilon. The weighted test uses frequency arrays to represent repeated samples and checks that the weighted path matches expected repeated-sample statistics.

Dependencies and integration: uses `math` and `testing` only. Risks not covered include standard deviation specifically, very large values/frequencies, negative values, NaN/Inf behavior, and whether the unused `w2Sum` should matter for an unbiased weighted estimator. The tests are valuable smoke tests for sample variance semantics because expected values explicitly use `M2/(n-1)`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/welford_test.go -->
