# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/ProxyServerIntegrationTest.java

## Purpose

This integration test verifies the standalone `ProxyServer` routing behavior. It starts three mock Jetty backends, starts the proxy, checks round-robin routing through the proxy, and checks that each backend remains directly reachable.

## Important APIs, types, and functions

The test uses Jetty `Server`, `ServletContextHandler`, `ServletHolder`, a local `ServiceServlet`, `ProxyServer`, `GenericTestUtils.waitFor()`, `HttpURLConnection`, and AssertJ assertions. Helpers include `startMockServer()`, `startProxy()`, `waitForMockServersStarted()`, `waitForProxyReady()`, and `sendRequest()`.

## Control flow, state, and persistence

`@BeforeAll` starts three mock servers on free localhost ports, each serving `/service-name` with its own name. It then starts a `ProxyServer` over those endpoints and records `proxyUrl`. `testRouting()` sends twice as many requests as servers and expects responses in modulo order. `testDirectAccess()` requests each backend URL directly and expects the matching server name. `@AfterAll` stops the proxy and all mock servers.

## Dependencies and integration points

The test exercises `ProxyServer`, `RoundRobinStrategy`, Jetty servlet plumbing, and Java URL connections. It does not involve Ozone or S3 Gateway, which keeps proxy routing failures isolated.

## Risks and test signals

The test assumes no concurrent tests share the same static proxy state and that free ports remain available until binding. It does not test POST bodies, headers, query strings, or failure handling. Positive signals are proxy startup readiness, direct backend responses, and deterministic round-robin sequence `server-0`, `server-1`, `server-2`, repeated.
