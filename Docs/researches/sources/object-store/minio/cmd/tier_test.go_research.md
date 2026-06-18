# sources/object-store/minio/cmd/tier_test.go

Purpose: hand-written unit test coverage for tier metrics reporting.

Important APIs and functions: `TestTierMetrics` exercises `globalTierMetrics.Observe`, `logSuccess`, `logFailure`, and `Report`. It refers to metric names `tierRequestsSuccess` and `tierRequestsFailure`.

Control flow: the test observes one latency sample for tier `WARM-1`, records ten successes and five failures, calls `Report`, then aggregates returned metric values by description name and asserts expected totals.

State and persistence: mutates package-level `globalTierMetrics`, especially its request counters and Prometheus histogram. There is no persistence. Because the global is shared, test ordering or repeated execution in the same process can affect counts if other tests mutate the same tier metric names.

Dependencies and integration points: depends on the metrics code in `tier.go` and MinIO's `MetricV2` descriptions. It indirectly checks that `Report` includes counter metrics alongside histogram output.

Risks: the test is narrow and uses a global counter map without reset, so additions of other tests using the same tier name could make it flaky. It does not assert histogram buckets or labels, only success/failure totals.

Test signals: provides a small but useful signal that tier success/failure counters are incremented and surfaced by `Report`.
