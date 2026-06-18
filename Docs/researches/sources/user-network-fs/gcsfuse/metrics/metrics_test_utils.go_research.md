## sources/user-network-fs/gcsfuse/metrics/metrics_test_utils.go

Purpose: Shared assertions for OpenTelemetry metric tests.

Important APIs/types/functions: `verifyConfig`, `VerifyOption`, `AtLeast`, `Subset`, `matchesAttributes`, `verifyValue`, `VerifyCounterMetric`, `VerifyHistogramMetric`, and `VerifyHistogramFull`.

Control flow: helpers collect from a `metric.ManualReader`, scan all scope metrics by name, match attribute sets exactly or as subset, assert values exactly or at least, and support integer/float histograms with optional bucket verification.

State and persistence behavior: reads metric data from in-memory OpenTelemetry reader; no persistence.

Dependencies and integration points: used by metrics implementation tests to verify generated instruments without duplicating OpenTelemetry traversal code.

Risks: helpers fail on the first matching data point and do not aggregate multiple data points. Exact attribute encoding depends on OpenTelemetry encoder behavior.

Test signals: these are test support utilities; reliability affects all metrics tests.
