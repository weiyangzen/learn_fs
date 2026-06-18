# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithNativeLib.java

Purpose: This concrete subclass runs the shared `TestOmSnapshot` suite for file-system-optimized buckets with RocksDB native diff tooling enabled. It is the native-diff FSO matrix entry.

Important APIs/types/functions: The class extends `TestOmSnapshot`, uses `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and is gated by `@EnabledIfSystemProperty(named = ROCKS_TOOLS_NATIVE_PROPERTY, matches = "true")`. Its constructor calls `super(FILE_SYSTEM_OPTIMIZED, false, false, false, false)`.

Control flow: JUnit only instantiates this class when the native tools system property is true. Construction delegates all setup and tests to `TestOmSnapshot`, with filesystem paths disabled, full diff disabled, native diff enabled, and linked bucket creation disabled.

State and persistence behavior: The state behavior comes from the inherited suite: FSO directory/file tables, snapshot checkpoint creation, native RocksDB checkpoint differ and compaction DAG behavior, and snapshot diff outputs across FSO namespace mutations.

Dependencies and integration points: This subclass depends on native RocksDB tools availability and the shared MiniOzone setup in `TestOmSnapshot`. It is the canonical class for native-only heavyweight tests such as compaction DAG coverage when `assumeCanonicalConfig(true)` is used.

Risks and edge cases: If the system property is not set, this matrix entry does not run. If native libraries fail to load after the property gate, inherited assumptions skip native-dependent paths. The subclass itself is intentionally minimal, so constructor argument drift would silently change a large inherited test surface.

Test signals: Passing signals are inherited from `TestOmSnapshot`, especially native diff and compaction DAG assertions under FSO layout.
