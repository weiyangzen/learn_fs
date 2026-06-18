## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/PrometheusServiceProviderImpl.java

Purpose: this provider implements `MetricsServiceProvider` for Prometheus HTTP API queries.

Important APIs and types: constructor reads `OZONE_RECON_PROMETHEUS_HTTP_ENDPOINT`, stores `URLConnectionFactory` and `ReconUtils`, and trims trailing slash. `getMetricsResponse`, static `getEndpointConfigKey`, `getMetricsInstant`, and private `getMetrics` implement the Prometheus path. General `getMetrics(String)` returns an empty list.

Control flow: `getMetricsResponse` builds `<endpoint>/api/v1/<api>?<queryString>` and performs an HTTP call without Kerberos. `getMetricsInstant` uses API `query`. The parser checks successful HTTP status, parses JSON with Jackson, requires status `success`, reads `data.resultType`, chooses `value` for vector or `values` for matrix, converts timestamp/value pairs into `TreeMap<Double,Double>`, and wraps metadata plus values in `Metric`.

State and persistence: no persistence. Holds endpoint/client utilities only.

Dependencies and integration points: used by Recon metrics APIs when Prometheus is configured. Depends on Prometheus response schema and Recon's `Metric` type.

Risks and edge cases: returns `null` metrics when a successful response has empty result or unsupported shape, so callers must handle null as well as empty. Query strings are not URL encoded. The code assumes timestamps are `Double` and values are numeric strings. Non-success status logs errors but does not throw.

Test signals: tests should cover endpoint trimming, URL construction, vector and matrix parsing, empty result behavior, Prometheus error payload logging, and HTTP failure handling.
