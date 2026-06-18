# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/ProxyServer.java

## Purpose

This class implements a Jetty reverse proxy for S3 Gateway endpoints. It selects a backend endpoint per request using a `LoadBalanceStrategy`, rewrites the target URL, and forwards the request to the selected S3G.

## Important APIs, types, and functions

The class owns endpoint list, load-balancing strategy, Jetty `Server`, host, and port. Constructors default to `RoundRobinStrategy` unless a strategy is supplied. Lifecycle methods are `start()`, `stop()`, and `isStarted()`. The inner `ProxyHandler` extends `ProxyServlet.Transparent` and overrides `init()`, `rewriteTarget()`, `service()`, `onProxyResponseFailure()`, and `onProxyRewriteFailed()`.

## Control flow, state, and persistence

The constructor creates a Jetty server on the proxy port, installs a servlet context at `/`, and maps `ProxyHandler` to `/*`. For each request, `rewriteTarget()` chooses a base URL, appends request URI and query string, and returns the target. `service()` wraps requests containing an `Expect` header so the proxy sees that header as absent, avoiding Jetty 100-continue handling issues observed in S3 put-object tests. Failures are logged and rewrite failure attempts to send HTTP 502 text.

## Dependencies and integration points

It depends on Jetty server/servlet/proxy/client APIs, Guava `HttpHeaders`, servlet request wrappers, and `LoadBalanceStrategy`. It is used by `MultiS3GatewayService` for real S3 Gateway tests and by `ProxyServerIntegrationTest` with mock backends.

## Risks and test signals

The endpoint list is accepted without constructor validation; null or empty lists fail later in the strategy. The proxy binds `new Server(proxyPort)` without the host, so the host parameter is mostly informational. Removing `Expect` is a test compatibility workaround that may hide behavior differences for clients relying on 100-continue semantics. Positive signals include correct URL rewriting with query strings, round-robin distribution, successful direct and proxied GETs, useful failure logs, and no hangs on requests with `Expect`.
