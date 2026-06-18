# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/RemoveEmptyValueCompactionFilterFactory.java

Purpose: Test fixture factory that produces `RemoveEmptyValueCompactionFilter` instances for RocksJava compaction-filter tests.

Important APIs/types/functions: extends `AbstractCompactionFilterFactory<RemoveEmptyValueCompactionFilter>`, implements `createCompactionFilter(AbstractCompactionFilter.Context)` and `name()`.

Control flow and state: `createCompactionFilter` ignores the supplied compaction context and returns a new `RemoveEmptyValueCompactionFilter` on each factory invocation. `name()` returns a stable descriptive name.

State and persistence behavior: no internal mutable state is stored. Persistence effects are delegated to the returned compaction filter, which removes entries with empty values during compaction in consuming tests.

Dependencies and integration points: integrates with RocksJava native compaction filter factory callbacks and is consumed by tests that set a compaction filter factory on options.

Risks: context is ignored, so it cannot vary behavior by full/manual compaction or column family. The factory allocates a new filter every call and relies on RocksJava/native ownership handling.

Test signals: this file is itself a helper, not a test; its correctness is signaled by downstream compaction filter tests.
