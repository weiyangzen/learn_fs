# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/LoadBalanceStrategy.java

## Purpose

This interface defines the pluggable strategy used by the S3 test proxy to choose an S3 Gateway endpoint for each incoming request.

## Important APIs, types, and functions

It declares one method: `String selectEndpoint(List<String> endpoints)`. Implementations receive the current list of available endpoint base URLs and return the selected target base URL.

## Control flow, state, and persistence

The interface has no state or implementation. State and concurrency behavior are delegated to implementations such as `RoundRobinStrategy`.

## Dependencies and integration points

`ProxyServer.ProxyHandler.rewriteTarget()` calls this method on every proxied request before appending the request URI and query string. `MultiS3GatewayService` supplies the endpoint list when constructing `ProxyServer`.

## Risks and test signals

Implementations must handle null or empty endpoint lists consistently; the interface does not specify exception behavior beyond the Java signature. Positive signals are deterministic endpoint selection in `ProxyServerIntegrationTest` and easy substitution of alternative strategies for future S3 Gateway load-balancing tests.
