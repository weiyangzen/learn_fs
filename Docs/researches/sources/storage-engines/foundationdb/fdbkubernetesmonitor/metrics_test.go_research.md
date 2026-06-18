# sources/storage-engines/foundationdb/fdbkubernetesmonitor/metrics_test.go

Purpose: unit tests for the monitor Prometheus metric registration and update methods. It documents expected collector counts, labels, counter values, and version gauge reset behavior.

Important APIs and functions: tests create a fresh `prometheus.Registry`, call `registerMetrics`, then exercise `registerConfigurationChange` and `registerProcessStartup`. Gathered metric families are inspected with suffix checks against metric name constants and label constants.

Control flow: tests start with no custom metric observations, then add one or more configuration changes or process starts. Nested contexts check same-version and different-version transitions.

State and persistence behavior: all state is transient in a per-test registry. The tests verify cumulative counters and current-version gauges, including zeroing of previous version gauges after a version change.

Dependencies and integration points: uses Ginkgo/Gomega, Prometheus registry APIs, and Kubernetes pointer helpers for metric family names. It is tightly coupled to the names and labels in `metrics.go`.

Risks: tests assert metric family counts, which may be brittle if Prometheus client behavior changes or additional collectors are registered. They do not verify timestamp gauge values beyond collector presence.

Test signals: strong for restart count increments, process label values, desired/running version labels, and preservation of old version series at value zero.
