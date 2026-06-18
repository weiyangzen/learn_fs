<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/MetricsProxyEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/MetricsProxyEndpoint.java

## Purpose

`MetricsProxyEndpoint` proxies Recon UI/API metric requests to the configured external metrics provider, normally Prometheus.

## Important APIs and Types

The endpoint is mounted at `/metrics/{api}`. `getMetricsResponse` receives the API path component and current query string, obtains an `HttpURLConnection` from `MetricsServiceProvider`, and streams the provider response to `HttpServletResponse` using NIO channels.

## Control Flow

If a provider exists, the method calls `getMetricsResponse(api, query)`. Successful 2xx responses stream `connection.getInputStream`; non-2xx provider responses set Recon's response status to 502 and stream `connection.getErrorStream`. If no provider is configured, Recon sends a 502 with the Prometheus endpoint config key in the message.

## State and Persistence

The endpoint stores only the injected provider reference. It persists nothing.

## Dependencies and Integration Points

It depends on `MetricsServiceProviderFactory`, `MetricsServiceProvider`, and `PrometheusServiceProviderImpl` constants/config. It is an integration bridge between Recon's REST namespace and Prometheus-compatible HTTP APIs.

## Risks and Edge Cases

The path parameter allows arbitrary provider API suffixes supported by the provider implementation. Error streams may be null for some `HttpURLConnection` failures, which would make channel creation fail. It does not copy content type or headers from Prometheus, only body and coarse status behavior. Provider connections must enforce their own timeout behavior.

## Test Signals

Tests should mock 2xx and non-2xx provider responses, null provider behavior, query-string forwarding, large body streaming, and missing error-stream handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/MetricsProxyEndpoint.java -->
