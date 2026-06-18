## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/MetricsServiceProvider.java

Purpose: `MetricsServiceProvider` abstracts Recon's access to external metrics systems such as JMX and Prometheus.

Important APIs and types: declares `getMetricsResponse(String api, String queryString)`, `getMetricsInstant(String queryString)`, and `getMetrics(String queryString)`. Return types are `HttpURLConnection`, `List<Metric>`, and `List<Map<String,Object>>`.

Control flow: implementations choose how to build URLs, authenticate, parse response payloads, and map metrics to Recon API shapes.

State and persistence: no state in the interface. Implementations hold endpoint/config/client state but do not persist metrics here.

Dependencies and integration points: implemented by `JmxServiceProviderImpl` and `PrometheusServiceProviderImpl`. API resources can depend on this SPI without knowing the backend.

Risks and edge cases: the interface mixes raw connection access with parsed metrics, and implementations return empty lists for unsupported query styles. Callers must know which method is meaningful for the selected provider.

Test signals: tests should be implementation-specific, verifying URL construction, HTTP status handling, parser behavior, and unsupported method behavior.
