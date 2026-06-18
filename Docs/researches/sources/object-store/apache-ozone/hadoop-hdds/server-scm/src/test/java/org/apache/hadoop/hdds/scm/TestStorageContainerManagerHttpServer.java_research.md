# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHttpServer.java

## Purpose

This parameterized JUnit 5 test verifies that `StorageContainerManagerHttpServer` exposes HTTP and HTTPS endpoints according to each `HttpConfig.Policy`. It confirms that SCM binds ephemeral local ports and that enabled schemes serve `/jmx` while disabled schemes are not reachable.

## Important APIs, Types, and Functions

- `setUp` creates SSL test material with `KeyStoreTestUtil.setupSSLConfig`, configures Ozone client/server keystore resources, and initializes a `URLConnectionFactory`.
- `testHttpPolicy(HttpConfig.Policy policy)` iterates all HTTP policies via `@EnumSource`.
- `StorageContainerManagerHttpServer.start/stop`, `getHttpAddress`, and `getHttpsAddress` are the production APIs under test.
- `canAccess` opens a URL to `/jmx` through the configured connection factory.
- `implies` keeps assertions compact for policy-dependent access rules.

## Control Flow and State Behavior

For each policy, the test updates `OZONE_HTTP_POLICY_KEY`, sets HTTP and HTTPS bind and advertised addresses to `localhost:0`, initializes the Hadoop metrics system, starts the SCM HTTP server, and probes the published addresses. Assertions encode both positive and negative policy expectations: HTTP-only should not expose HTTPS, HTTPS-only should not expose HTTP, and dual-enabled policy should expose both.

## State and Persistence

The test writes temporary metadata and SSL keystore configuration under JUnit `@TempDir`. It cleans SSL configuration and destroys the connection factory in `tearDown`. There is no SCM metadata persistence beyond temporary directories.

## Dependencies and Integration Points

The file depends on Ozone configuration keys, SCM HTTP address keys, Hadoop `HttpConfig.Policy`, `DefaultMetricsSystem`, `URLConnectionFactory`, `NetUtils`, and `KeyStoreTestUtil`. It is an integration-style test for SCM web server startup and TLS wiring.

## Risks and Test Signals

The main risks are false negatives from local networking, stale metrics system state, or SSL setup failures. The strongest signal is end-to-end connection to `/jmx` through the same URL connection stack clients use, proving bind address, policy, and keystore configuration work together.
