# sources/storage-engines/rocksdb/db/wide/wide_column_serialization_test.cc

Purpose: This is the main unit-test coverage for RocksDB wide-column serialization. It exercises `WideColumn`, `WideColumnSerialization`, V1/V2 entity encodings, blob-column references, V2 fallback behavior in `PinnableWideColumns`, default-column lookup, resolved-entity serialization, and randomized round trips.

Important APIs/types/functions: `WideColumnSerializationTest` exposes friend-access wrappers for private `GetVersion` and `SerializeResolvedEntity`. Local helpers build `BlobIndex` values, convert string pairs to `WideColumns`, serialize and deserialize V2 entities, verify default-column extraction, and generate random blob indexes. Tests cover `Serialize`, `Deserialize`, `SerializeV2`, `DeserializeV2`, `HasBlobColumns`, `GetValueOfDefaultColumn`, `ResolveEntityForMerge`, and `BlobIndex::EncodeTo`.

Control flow: The tests start with construction and V1 serialize/deserialize, then drive corrupt input paths by incrementally appending malformed V1/V2 buffers. V2 tests manually construct binary layouts, verify out-of-order and recursive entity rejection, serialize inline/blob column mixes, deserialize them through V2-specific APIs, and check when generic `Deserialize` must reject unresolved blob references with `NotSupported`. Randomized tests generate sorted unique column names and values, randomly mark columns as blob-backed, then assert V2 metadata, blob-index round trip, optional V1 compatibility, and the Slice-based overload behavior.

State and persistence behavior: The file models wide-column entities as serialized bytes stored in write batches, memtables, or SST/blob layers. It checks binary format version persistence, column order invariants, blob-reference metadata preservation, and resolved entity downgrade to V1 once blob values are fetched. `PinnableWideColumnsFallbacksToV2` verifies persisted V2 bytes can populate the column index while tracking unresolved blob columns.

Dependencies and integration points: It depends on `db/wide/wide_column_serialization.h`, `db/wide/wide_columns_helper.h`, `db/blob/blob_index.h`, `rocksdb/wide_columns.h`, `util/coding.h`, and RocksDB test harness/random utilities. It is tightly coupled to the serialized V2 layout consumed by write batches, merge resolution, blob reads, and `PinnableWideColumns`.

Risks: Tests rely on hand-built buffers matching exact layout order; layout changes require coordinated updates. Randomized tests seed from wall-clock time, so failures need the printed scoped trace seed for reproduction. Inlined TTL blob indexes are avoided in one helper because their slices can dangle after local encoded storage is destroyed.

Test signals: Strong coverage exists for valid/invalid V1 and V2 parsing, duplicate/out-of-order columns, unsupported recursive value types, blob references, default-column fast paths, encode/decode round trips, and null blob fetcher error handling.
