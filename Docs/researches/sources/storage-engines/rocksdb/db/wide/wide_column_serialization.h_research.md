# sources/storage-engines/rocksdb/db/wide/wide_column_serialization.h

Purpose: Declares `WideColumnSerialization`, the internal static utility that owns RocksDB's wide-column entity serialization contract. The header documents V1 and V2 layouts and exposes APIs for writing, reading, blob-reference inspection, default-column extraction, and blob resolution.

Important APIs/types/functions: Constants `kVersion1` and `kVersion2` identify the supported formats. Public methods include `Serialize`, `SerializeV2`, `Deserialize`, `DeserializeV2`, `HasBlobColumns`, `ForEachBlobFileNumber`, `GetValueOfDefaultColumn`, `ResolveEntityBlobColumns`, `GetValueOfDefaultColumnResolvingBlobs`, and `ResolveEntityForMerge`. Private helpers cover version parsing, resolved-entity serialization, `uint32_t` size validation, strict column-order validation, templated V2 serialization, blob-index map construction, V1/V2 parsing, supported `ValueType` validation, and blob-type scanning.

Control flow contract: Producers serialize sorted `WideColumns`; if any columns are stored externally, they call V2 serialization with a list of `(column_index, BlobIndex)` entries. Consumers can use `Deserialize` for all-inline entities, `DeserializeV2` when blob references are possible, `HasBlobColumns` for a cheap type-byte check, and `ForEachBlobFileNumber` for lightweight blob-file discovery. Merge/read compatibility helpers resolve blob references and produce an effective all-inline V1 entity when required.

State and persistence behavior: The header is the durable format specification. V1 stores version, column count, column names and value sizes, then values. V2 stores version/count, skip-info byte lengths, per-column type bytes, name-size varints, value-size varints, names, and values or blob-index encodings. The skip-info design allows default-column and type checks without scanning every variable-length name/value field. No runtime state is owned by the class.

Dependencies: The declaration depends on `db/dbformat.h` for `ValueType`, RocksDB `Status`, `Slice`, `WideColumns`, blob-related forward declarations, `PrefetchBufferCollection`, `PinnableSlice`, standard `function`, `limits`, and vectors of blob-index metadata.

Integration points: The API is used by DB write paths, write batches, memtables/SST values, read paths, merge paths, compaction/blob GC, and tests. It bridges wide-column semantics to blob storage by treating serialized `BlobIndex` values as per-column payloads in V2. The resolving APIs are compatibility shims for consumers that still require V1 all-inline entity bytes.

Risks and edge cases: Because this header defines on-disk bytes, any layout change must preserve backward compatibility. `kTypeWideColumnEntity` is intentionally rejected as a per-column type to avoid recursive entities. Callers must choose resolving APIs whenever blob-backed default columns or merge bases are possible. Deserialized slices reference the input buffer, so lifetime management belongs to callers.

Test signals: The contract is covered by the wide-column basic and direct-write suites in this subset: duplicate-column errors, V1 round trips, V2 blob references, default-column extraction, merge resolution, blob-file-number accounting, direct-write serialized-blob rejection, cache-tier incomplete reads, and read-only recovery of blob-backed entities.
