# sources/object-store/minio/cmd/metrics-v3-cluster-iam.go

Purpose: Exposes v3 IAM and external auth plugin health/sync metrics.

Important APIs/types/functions: Defines metrics for IAM sync duration, time since last sync, sync successes/failures, plugin auth request totals/failures, last success/failure seconds, and average/max successful RTT. `loadClusterIAMMetrics` populates all values.

Control flow: The loader reads IAM atomics from `globalIAMSys`, gets plugin auth metrics from `globalAuthNPlugin.Metrics()`, computes milliseconds since last sync if a last sync timestamp exists, and stores all values in `MetricValues`.

State and persistence behavior: Stateless loader over global atomics and plugin state. Counters are process-lifetime values and timing gauges reflect current wall-clock deltas.

Dependencies and integration points: Depends on `globalIAMSys`, `globalAuthNPlugin`, `sync/atomic`, and v3 metric descriptors. It is a v3 replacement for IAM metrics in the v2 monolithic file.

Risks: The loader assumes `globalIAMSys` and `globalAuthNPlugin` are initialized by the metric group dependency setup. Several descriptors use `NewCounterMD` for values that behave like gauges or durations, so metric type semantics should be reviewed before dashboard or alert changes.

Test signals: No direct tests in this subset.
