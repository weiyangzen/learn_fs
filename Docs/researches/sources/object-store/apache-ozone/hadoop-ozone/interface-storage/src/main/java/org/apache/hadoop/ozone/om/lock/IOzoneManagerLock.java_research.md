# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/IOzoneManagerLock.java

Purpose: Primary interface for Ozone Manager metadata locks, including read/write keyed locks, resource locks, multi-user locks, metrics, and testing hooks.

Important APIs/types/functions: Methods acquire/release read and write locks for single or multiple resource key arrays, acquire/release resource write locks, acquire/release multi-user locks, inspect hold counts and current-thread ownership for tests, `cleanup()`, and `getOMLockMetrics()`. Default helpers `acquireResourceLock` and `acquireLock` return `UncheckedAutoCloseableSupplier<OMLockDetails>` wrappers that release once on close. Nested `Resource` provides name and `ResourceManager`; nested `ResourceManager` tracks per-thread read/write held-time start nanos via `ThreadLocal<LockUsageInfo>`.

Control flow, state, and persistence: Implementations perform actual locking. Default helper methods acquire, validate success, and protect release with `AtomicBoolean` to make close idempotent. Resource timing state is thread-local and removed when retrieved, supporting metrics for lock wait/hold durations. No persistence occurs.

Dependencies and integration points: Used across OM request handlers and metadata managers to protect namespace tables. Integrates with `OMLockDetails`, `OMLockMetrics`, `LockUsageInfo`, Ratis unchecked closeable supplier, and resource enums such as `DAGLeveledResource`.

Risks: Lock ordering and release symmetry are critical. Default helpers throw `RuntimeException` if acquisition fails, so callers must be prepared for unchecked failure. ThreadLocal timestamp removal on getter means metrics code must call it exactly when releasing; missed or repeated calls can lose timing data.

Test signals: Interface-specific implementation tests are elsewhere. This subset has lock DAG tests and `OMLockDetails` proto fields in `OmClientProtocol.proto` for response/debug integration.
