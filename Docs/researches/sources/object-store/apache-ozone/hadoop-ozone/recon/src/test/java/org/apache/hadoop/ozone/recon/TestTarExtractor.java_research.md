# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestTarExtractor.java

## Purpose
This JUnit/Mockito test verifies `TarExtractor` executor lifecycle behavior: pool creation, thread naming, shutdown, and idempotent start.

## Important APIs and functions
`testStartCreatesFixedThreadPoolWithConfiguredSize` mocks static `Executors.newFixedThreadPool` and verifies the configured pool size. `testThreadFactoryUsesConfiguredPrefix` captures the `ThreadFactory` and asserts created thread names start with the configured prefix. `testStopShutsDownExecutor` verifies `shutdown` after `stop`. `testStartIsIdempotent` calls `start` twice and verifies only one executor is created.

## Control flow, state, and persistence
The tests are in memory and use Mockito static mocking. `TarExtractor` is constructed outside the static mock block so its internal thread factory builder can call the real default factory. Shutdown behavior stubs `awaitTermination`.

## Dependencies and integration points
Dependencies include JUnit 5 and Mockito static mocking. This indirectly protects Recon code that uses `TarExtractor` to parallelize snapshot tar extraction.

## Risks and edge cases
The tests do not submit extraction tasks or verify forced shutdown on timeout/interruption. Static mocking of `Executors` is sensitive to construction ordering, which the comments explicitly call out.

## Test signals
Good lifecycle regression coverage for concurrency setup. Functional tar extraction behavior is covered separately by `TestReconUtils`.
