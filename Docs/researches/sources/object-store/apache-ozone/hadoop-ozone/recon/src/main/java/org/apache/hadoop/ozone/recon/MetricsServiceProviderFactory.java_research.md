# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/MetricsServiceProviderFactory.java

## Purpose
`MetricsServiceProviderFactory` selects and constructs Recon metrics-provider implementations for Prometheus and JMX-backed metric collection.

## Important APIs, Types, And Functions
The constructor reads metrics HTTP timeouts and creates a `URLConnectionFactory`. `getMetricsServiceProvider()` returns a `PrometheusServiceProviderImpl` when `OZONE_RECON_PROMETHEUS_HTTP_ENDPOINT` is configured. `getJmxMetricsServiceProvider(String)` always creates a `JmxServiceProviderImpl`.

## Control Flow
On construction it converts timeout configs to milliseconds. Prometheus selection trims a trailing slash from the endpoint, logs the selected provider, and returns null when no endpoint is configured.

## State And Persistence
Runtime state is the injected `OzoneConfiguration`, `ReconUtils`, and connection factory. No metrics are persisted by this class.

## Dependencies And Integration Points
It is a singleton Guice binding used by `DataNodeMetricsService` and metric collection tasks. It depends on HDFS `URLConnectionFactory`, Recon config keys, `ReconUtils`, and provider implementations.

## Risks
Prometheus selection only checks non-empty endpoint string; endpoint reachability and authentication failures surface later. Connection timeout values are cast to int milliseconds and can overflow if configured extremely high.

## Test Signals
Tests should cover absent endpoint returning null, trailing slash normalization, timeout propagation, Prometheus provider creation, and JMX provider creation.
