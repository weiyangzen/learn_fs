# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestOzoneManagerLock.java

Purpose: broad unit coverage for `OzoneManagerLock`, including leveled lock ordering, DAG-style snapshot lock ordering, read/write/resource lock contention, multi-user locking, hold counts, and lock metrics.

Important APIs/types: `OzoneManagerLock`, `IOzoneManagerLock.Resource`, `OzoneManagerLock.LeveledResource`, `DAGLeveledResource`, `OMLockMetrics`, `MetricsCollectorImpl`, and generated resource names. Helper `ResourceInfo` records lock resources for stack-based release in reverse order.

Control flow: parameterized tests acquire and release every leveled resource; reacquire tests distinguish non-reentrant resources (`USER_LOCK`, `S3_SECRET_LOCK`, `PREFIX_LOCK`) from reentrant locks. Ordering tests acquire lower-level then higher-level locks, while violation tests attempt the inverse and assert runtime error messages. DAG tests encode forbidden edges for snapshot DB/content/local/GC/bootstrap locks. Contention tests start secondary threads and use `AtomicBoolean` plus short sleeps to verify blocking until release. Metrics tests run concurrent readers/writers and assert sample counts.

State and persistence behavior: no disk persistence. The important state is thread-local lock ownership, lock hold counts, resource-wide locks, and metrics histograms for waiting/held time.

Dependencies and integration points: depends on Ozone configuration, Hadoop metrics, JUnit parameterized tests, AssertJ, and Java concurrency. It is a behavioral contract for OM metadata mutation ordering and snapshot-related lock sequencing.

Risks: sleep-based concurrency checks can be timing-sensitive. Error message assertions are useful but couple tests to wording. Multi-resource lock tests rely on generated UUID names and do not cover every real OM key path shape.

Test signals: strong coverage of allowed and forbidden lock order, same-thread reentrancy policy, cross-thread exclusion, multi-lock collision, resource-wide lock conflicts, and metrics export fields.
