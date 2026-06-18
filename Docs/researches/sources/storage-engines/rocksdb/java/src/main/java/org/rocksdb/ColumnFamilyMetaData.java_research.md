# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyMetaData.java

- **Purpose:** Immutable metadata snapshot describing a column family's size, file count, name, and per-level metadata.
- **Important APIs/types/functions:** Private JNI constructor sets final fields. Public accessors are `size()`, `fileCount()`, `name()`, and `levels()`.
- **Control flow:** Native code constructs instances when metadata APIs are called. `levels()` wraps the backing array with `Arrays.asList`.
- **State and persistence behavior:** Stores a point-in-time Java snapshot of native LSM metadata. It does not own native resources or mutate DB state.
- **Dependencies:** Depends on `LevelMetaData`, `Arrays`, and `List`.
- **Integration points:** Returned by RocksDB column-family metadata APIs for diagnostics, monitoring, and tests.
- **Risks:** `name()` returns the internal byte array; `levels()` returns a fixed-size list backed by the internal array. Metadata can become stale immediately after DB activity.
- **Test signals:** Metadata values after writes/flushes/compactions, level list contents, file count/size consistency, and immutability/staleness expectations.
