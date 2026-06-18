# sources/storage-engines/foundationdb/fdbserver/core/ServerCheckpoint.cpp

## sources/storage-engines/foundationdb/fdbserver/core/ServerCheckpoint.cpp

Purpose: central dispatch for server-side checkpoint lifecycle operations. It hides checkpoint format differences from callers that need readers, deletion, full fetch, range fetch, or deterministic local directory naming.

Important APIs: `newCheckpointReader`, `deleteCheckpoint`, `fetchCheckpoint`, `fetchCheckpointRanges`, `serverCheckpointDir`, and `fetchedCheckpointDir`. The only implemented formats are RocksDB-backed: `DataMoveRocksCF`, `RocksDB`, and the range-fetch `RocksDBKeyValues` wrapper. Unsupported formats throw `not_implemented`.

Control flow and state: reader creation delegates to `newRocksDBCheckpointReader`. Deletion yields at `TaskPriority::FetchKeys`, then recursively erases `checkpoint.dir` when present and logs a warning if the metadata lacks a directory. Full fetch asserts it is not already a `RocksDBKeyValues` checkpoint, then delegates to `fetchRocksDBCheckpoint` and traces begin/end by checkpoint UID. Range fetch validates non-empty ranges, converts `DataMoveRocksCF` metadata into `RocksDBKeyValues` metadata by setting `ranges`, `dir`, and serialized `RocksDBCheckpointKeyValues`, then fetches through the same RocksDB path.

Dependencies and integration: depends on `ServerCheckpoint.h`, `RocksDBCheckpointUtils.h`, Flow actors, `ObjectWriter`, deterministic random UIDs, and platform directory deletion. It is used by storage fetch/checkpoint transfer paths and data movement that fetch full or range-limited SST checkpoints.

Risks and tests: format dispatch is intentionally narrow; adding another checkpoint format requires all four operations. Range fetch mutates the input metadata copy before serialization, so metadata compatibility matters. Directory deletion is irreversible and should be tested with missing-dir, unsupported-format, RocksDB, and range-limited checkpoint transfer simulations.
