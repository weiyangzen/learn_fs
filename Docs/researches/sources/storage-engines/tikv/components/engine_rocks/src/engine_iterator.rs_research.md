<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/engine_iterator.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/engine_iterator.rs

Purpose: wraps RocksDB iterators in the engine abstraction and exposes iterator perf counters.

Important APIs/types/functions: `RocksEngineIterator`, `from_raw`, `RocksIterMetricsCollector`, `MetricsExt`, and `engine_traits::Iterator` methods.

Control flow: seek operations translate engine calls to RocksDB `SeekKey`; movement calls guard against invalid iterators unless `nortcheck` is enabled; key/value access asserts validity in checked builds.

State and persistence behavior: holds a RocksDB iterator over an `Arc<DB>` and reads a consistent Rocks iterator view according to the read options used during construction. No persistent state is modified.

Dependencies/integration: created by `RocksEngine::iterator_opt`; metrics pull from RocksDB thread-local `PerfContext`.

Risks: invalid iterator movement returns errors or panics depending on feature flags; callers must respect iterator validity before accessing key/value. Metrics are thread-local and only meaningful when perf context is configured.

Test signals: iterator behavior is exercised by scan/seek tests in `engine.rs` and delete-range tests in `misc.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/engine_iterator.rs -->
