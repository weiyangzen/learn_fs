# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotMetrics.java

Purpose: `OmSnapshotMetrics` is the metrics source used by snapshot metadata readers. It counts read-only key, filesystem, ACL, listing, and object-tagging operations against snapshots and their failures.

Important APIs/types/functions: The class is `@Metrics(context = "dfs")`, implements `OmMetadataReaderMetrics`, and exposes a singleton through `getInstance()`. It registers itself with `DefaultMetricsSystem` under the source name `OmSnapshotMetrics` using a `MemoizedSupplier`. Metric fields are `MutableCounterLong` counters annotated with `@Metric`, including per-operation counters plus aggregate `numKeyOps` and `numFSOps`.

Control flow: The private constructor prevents direct construction. The first `getInstance()` call registers the source with the default Hadoop metrics system; subsequent calls return the memoized instance. Each `inc...` method increments the operation-specific counter, and selected methods also increment aggregate counters. Key lookup, key info, list status, file status, lookup file, and object-tagging calls increment `numKeyOps`; list status, file status, and lookup file also increment `numFSOps`. Failure methods increment only failure counters.

State and persistence behavior: State is in-memory metrics-system counter state. There is no RocksDB or filesystem persistence. The singleton lifetime follows the process metrics system, so counters accumulate for the registered OM process unless the metrics system is reset by tests or process restart.

Dependencies/integration points: The class depends on Hadoop metrics2 (`MetricsSystem`, `DefaultMetricsSystem`, `MutableCounterLong`) and the `OmMetadataReaderMetrics` contract shared by active and snapshot metadata readers. Snapshot `KeyManagerImpl`, prefix manager, and metadata-reader paths can use this object to account operations performed against snapshot DBs separately from active OM metrics.

Risks: The counters rely on metrics2 injection during registration; calling increment methods on an unregistered manually constructed instance would leave fields null, but construction is private and `getInstance` registers it. Aggregate counters are hand-maintained, so new operations added to `OmMetadataReaderMetrics` need deliberate aggregate updates. Failure counters do not increment aggregate operation counters, which is a semantic choice that consumers must understand.

Test signals: There is no direct test found for this file in the searched subset. Indirect signals are metrics registration through snapshot metadata-reader construction and assertions in broader snapshot read/list/get-file-status tests that drive the corresponding reader APIs without metrics-related null pointer failures.
