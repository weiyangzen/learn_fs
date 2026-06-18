# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/RoundRobinStrategy.java

## Purpose

This class implements the default load-balancing strategy for the test S3 proxy. It cycles through endpoint URLs in round-robin order.

## Important APIs, types, and functions

It implements `LoadBalanceStrategy` and defines `selectEndpoint(List<String> endpoints)`. An `AtomicInteger counter` stores the next index and is updated with `getAndUpdate(i -> (i + 1) % endpoints.size())`.

## Control flow, state, and persistence

Each call validates that the endpoint list is non-null and non-empty, atomically returns the current index, advances the counter modulo the current list size, and returns the endpoint at the chosen index. State is process-local and not persisted.

## Dependencies and integration points

`ProxyServer` uses this strategy by default. `ProxyServerIntegrationTest.testRouting()` indirectly verifies its behavior by expecting alternating backend names.

## Risks and test signals

Changing endpoint list size between calls can still work for normal size changes, but a concurrent empty list would throw. The atomic counter can overflow after enough requests; modulo update keeps indices bounded for usual operation, though negative overflow is avoided because the stored value remains modulo size. Positive signal is deterministic cycling through all configured endpoints under concurrent-safe atomic updates.
