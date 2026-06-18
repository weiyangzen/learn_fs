## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/JmxServiceProviderImpl.java

Purpose: this provider implements `MetricsServiceProvider` for Hadoop/Ozone JMX endpoints.

Important APIs and types: constructor stores `ReconUtils`, endpoint URL, `URLConnectionFactory`, and `OzoneConfiguration`. `getMetricsResponse` builds a query URL. `getMetrics` returns JMX `beans` as a list of maps. `getMetricsInstant` returns an empty list because JMX does not use Recon's `Metric` time-series shape here.

Control flow: endpoint trailing slash is trimmed. `getMetricsResponse` formats `<endpoint>?<api>=<queryString>` and calls `ReconUtils.makeHttpCall` with Kerberos determined from `HDDS_DATANODE_HTTP_AUTH_TYPE`. Private `getMetrics` runs as login user, checks for successful HTTP status, parses JSON using Hadoop `JsonUtils`, and returns the `beans` list when present.

State and persistence: no persistence. Holds HTTP client/config state and endpoint.

Dependencies and integration points: used wherever Recon is configured to fetch metrics from JMX rather than Prometheus. Uses Hadoop security utilities for SPNEGO/Kerberos execution.

Risks and edge cases: generic casts from JSON can fail if endpoint response shape changes. Non-success responses return empty lists without detailed exception. Query parameters are string-formatted without URL encoding. Kerberos detection uses datanode HTTP auth type.

Test signals: tests should cover URL trimming/construction, Kerberos flag behavior, successful beans parsing, non-success response handling, and unsupported instant-query empty result.
