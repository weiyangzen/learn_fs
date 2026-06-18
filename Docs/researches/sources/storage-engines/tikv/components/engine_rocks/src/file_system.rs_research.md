<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/file_system.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/file_system.rs

Purpose: wraps TiKV file-system IO inspection/rate limiting in a RocksDB environment.

Important APIs/types/functions: `get_env` and `WrappedFileSystemInspector<T>`.

Control flow: `get_env` starts from a provided or default RocksDB env, builds an `EngineFileSystemInspector` from an optional IO limiter, and creates an inspected RocksDB env. The wrapper forwards read/write byte requests and converts errors between engine and RocksDB representations.

State and persistence behavior: does not own durable state, but every RocksDB file read/write through the env can update limiter statistics and be throttled or accounted.

Dependencies/integration: layered after encryption by crate-level `get_env`; used by DB options during engine construction. Depends on `engine_traits`, `file_system`, and RocksDB env wrappers.

Risks: the wrapper only exposes read/write inspection; other filesystem operations rely on base env behavior. Incorrect IO type attribution from listeners would affect statistics classification.

Test signals: `test_inspected_compact` validates flush and compaction read/write accounting ranges against a test limiter.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/file_system.rs -->
