# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneClusterProvider.java

Purpose: Background pre-creation and asynchronous cleanup provider for mini-clusters used by test suites that need one cluster per test.

Important APIs/types/functions: Constructor accepts a configured `MiniOzoneCluster.Builder` and a `clusterLimit`, then starts create and reap threads. `provide()` returns a pre-created ready cluster, enforcing the limit. `destroy(MiniOzoneCluster)` queues a used cluster for shutdown. `shutdown()` interrupts creation, destroys remaining clusters, marks shutdown, and joins the reaper.

Control flow, state, and persistence: The create thread builds clusters until interrupted or limit reached, waits for readiness, and puts them into a single-slot queue. The reaper polls an expired-cluster queue and calls `shutdown()` without relying on interrupts. The provider tracks created/leased clusters in a set to clean up leftovers. Persistence belongs to the clusters it creates and is deleted by their shutdown.

Dependencies and integration points: Wraps `MiniOzoneCluster.Builder` and is intended for JUnit `BeforeAll`/`BeforeEach`/`AfterEach`/`AfterAll` workflows. Uses blocking queues, background threads, and SLF4J logging.

Risks: Methods are synchronized while potentially blocking on queue operations, so misuse can serialize test setup/teardown. Creation failures in the background thread become `RuntimeException`s that may surface asynchronously. The provider always tries to keep one cluster in reserve until the limit, so clusterLimit must match expected usage. `shutdown` sets the flag after destroying remaining clusters to allow reaper drain, which depends on queue polling.

Test signals: No direct tests in this subset. Integration-test runtime behavior is the primary signal: faster per-test cluster acquisition and reliable cleanup at suite shutdown.
