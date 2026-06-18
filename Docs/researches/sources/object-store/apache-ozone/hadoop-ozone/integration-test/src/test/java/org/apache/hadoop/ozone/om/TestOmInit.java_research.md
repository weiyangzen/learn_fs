# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmInit.java

## Purpose
Small integration test proving OM initialization is idempotent enough to run again after an already initialized MiniOzoneCluster OM is stopped.

## Important APIs, types, and functions
- Uses `MiniOzoneCluster.newBuilder(conf).build()` and `waitForClusterToBeReady()` to create a normal cluster.
- Calls `cluster.getOzoneManager().stop()` and then `OzoneManager.omInit(conf)`.
- JUnit lifecycle is static `@BeforeAll`/`@AfterAll`; assertion is `assertTrue`.

## Control flow
The class starts one MiniOzoneCluster for all tests, waits for readiness, stops the active OM in `testOmInitAgain`, then calls the static initialization path against the same configuration. Cleanup shuts the cluster down if it exists.

## State and persistence behavior
The test depends on metadata and VERSION files produced by the original cluster initialization. Re-running `omInit` should recognize existing storage and succeed rather than treating prior initialization as corruption or a fatal duplicate operation.

## Dependencies and integration points
It exercises `OzoneManager.omInit`, MiniOzoneCluster storage initialization, and Hadoop authentication exception plumbing. It is intentionally high-level and does not inspect the OM database directly.

## Risks and edge cases
Coverage is narrow: it only checks success after a clean `stop`, not partially initialized metadata, secure OM init, HA init, or failed prior initialization. Because it reuses cluster configuration, failures usually indicate a regression in storage init idempotency.

## Test signals
The only behavioral signal is that `omInit(conf)` returns `true` without throwing `IOException` or `AuthenticationException`.
