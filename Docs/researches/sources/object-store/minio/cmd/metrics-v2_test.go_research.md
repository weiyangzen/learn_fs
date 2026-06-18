# sources/object-store/minio/cmd/metrics-v2_test.go

Purpose: Unit tests for v2 histogram conversion in `getHistogramMetrics`.

Important APIs/types/functions: `TestGetHistogramMetrics_BucketCount` builds a `prometheus.HistogramVec`, records observations across several API labels, and checks that conversion emits one point per configured bucket plus one `+Inf` point per API label. `TestGetHistogramMetrics_Values` validates cumulative bucket counts and optional lowercasing of the `api` label.

Control flow: Tests create histograms, observe values with short ticker delays to exercise channel-based collection, call `getHistogramMetrics`, filter returned `MetricV2` values by API label, sort by the `le` label, and compare expected labels and counts.

State and persistence behavior: No persistent state. The tests rely on in-memory Prometheus histograms and fresh metric vectors per test. They indirectly test that `getHistogramMetrics` drains the collection channel and includes the synthetic `+Inf` sample.

Dependencies and integration points: Depends on Prometheus client histograms and the v2 metric descriptors from `metrics-v2.go`. It verifies compatibility behavior used by S3 and bucket TTFB v2 metrics.

Risks: The sort comparator appears to compare `a.VariableLabels["le"]` with itself instead of `b.VariableLabels["le"]`, so ordering checks may not be as deterministic as intended. The tests do not cover `limitBuckets=true` behavior or bucket-name capping, which is one of the v2 cardinality safeguards.

Test signals: Provides focused regression coverage for histogram expansion, API label casing compatibility, and cumulative count extraction.
