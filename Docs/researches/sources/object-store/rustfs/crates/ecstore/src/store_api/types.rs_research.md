# sources/object-store/rustfs/crates/ecstore/src/store_api/types.rs

## Purpose

`types.rs` defines the store API data model used by ecstore operations. It contains option structs for object requests, object metadata views, multipart/listing/delete result models, walking options, and helper logic for HTTP preconditions, actual-size calculation, compression/encryption metadata interpretation, version-marker pagination, replication state projection, and conversion from low-level `FileInfo` metadata into public `ObjectInfo`.

## Important APIs, Types, and Functions

- `HTTPPreconditions` stores `If-Match`, `If-None-Match`, `If-Modified-Since`, and `If-Unmodified-Since` values. Its private helpers ignore empty ETag condition strings.
- `ObjectLockRetentionOptions` models object-lock retention mode, retain-until time, and governance bypass.
- `ObjectOptions` is the central request option bag. It includes part selection, versioning flags, deletion flags, decommission/rebalance skips, replication/lifecycle/transition state, user metadata, preconditions, checksum options, and capacity-scope token.
- `ObjectOptions` methods update delete replication state, replica status, compute purge/delete-marker statuses, derive put replication state from metadata, and enforce preconditions with `precondition_check`.
- `MultipartUploadResult`, `PartInfo`, and `CompletePart` model multipart lifecycle data. `CompletePart` converts from `s3s::dto::CompletedPart`, preserving checksum fields.
- `ObjectInfo` is the main object metadata view. It includes bucket/name, storage class, mod time, logical and actual sizes, user metadata, erasure layout, version/delete-marker fields, transition and restore state, tags, parts, content fields, replication state, checksum bytes, and an optional `PutObjReader`.
- `ObjectInfo` methods detect compression/encryption, resolve compression read plans, compute encrypted/decrypted/actual sizes, convert from `FileInfo`, build listings from sorted metacache entries, project replication state, and expose checksum maps.
- `VersionMarker` and `versions_after_marker` implement null-version and UUID-version pagination for version listings.
- Listing/result models include `ListObjectsInfo`, `ListObjectsV2Info`, `MultipartInfo`, `ListMultipartsInfo`, `ListPartsInfo`, `ObjectToDelete`, `DeletedObject`, `ListObjectVersionsInfo`, `WalkOptions`, `WalkVersionsSortOrder`, and `ObjectInfoOrErr`.

## Control Flow

`ObjectOptions::precondition_check` first validates requested part number when multipart metadata is available. It then applies HTTP preconditions in S3/HTTP style: matching `If-None-Match` returns `NotModified`, `If-Modified-Since` returns `NotModified` when the object has not changed since the supplied timestamp, `If-Match` must match the object ETag or returns `PreconditionFailed`, and `If-Unmodified-Since` is checked only when `If-Match` is absent. ETag comparison strips quotes and treats `"*"` as a wildcard on the condition side.

`ObjectInfo::get_actual_size` prefers the explicit `actual_size` field. For compressed objects it then uses actual-size metadata, otherwise sums part `actual_size` values and errors if no actual size can be inferred while stored size is nonzero. For encrypted objects it checks RustFS and SSE-C original-size metadata, plus generic actual-size metadata, before falling back to stored `size`.

`ObjectInfo::from_file_info` converts low-level file metadata into API metadata. It decodes directory object names, assigns null UUIDs for unversioned entries in versioned buckets, extracts content headers and ETag, moves object tags into an `Arc<String>`, parses expiration metadata, projects replication state and status, constructs `TransitionedObject`, cleans internal metadata, chooses storage class, parses restore state, converts part metadata into `ObjectPartInfo`, and builds the final `ObjectInfo`.

`from_meta_cache_entries_sorted_versions` and `from_meta_cache_entries_sorted_infos` iterate sorted metacache entries, synthesize directory prefix entries when a delimiter is present, skip duplicate prefixes, convert object entries into `ObjectInfo`, and consult bucket versioning configuration. The versioned variant applies `after_version_marker` only to the first object entry by taking the marker option once, and skips entries with non-empty version purge status.

## State and Persistence Behavior

This file does not perform direct disk I/O, but it is the main projection layer for persistent object metadata. It reads metadata stored in `FileInfo`, including erasure information, part tables, replication internals, transition status, restore headers, tags, checksums, compression headers, encryption headers, and storage-class headers. It uses `Arc` for large cloned metadata fields (`user_defined`, `user_tags`, `parts`) and deliberately drops `put_object_reader` during `Clone` because streams cannot be cloned. Several result structs mirror S3 pagination state and must preserve marker/truncation fields accurately across calls.

## Dependencies and Integration Points

The module depends on the parent `store_api` prelude for domain types and constants. It integrates with `rustfs_filemeta` (`FileInfo`, `FileInfoVersions`, `MetaCacheEntriesSorted`, `ObjectPartInfo`, `ReplicationState`), bucket versioning config (`get_versioning_config`), lifecycle/transition types, replication status helpers, checksum parsing via `rustfs_rio::read_checksums`, storage class config constants, metadata cleanup and directory decoding helpers, and HTTP metadata helpers from `rustfs_utils`. The S3 API layer consumes these structs to build responses, while storage implementations consume `ObjectOptions` to decide behavior.

## Risks and Edge Cases

- `ObjectOptions` is large and loosely grouped; incompatible flags can be set together unless individual operations validate them.
- `ObjectInfo::is_encrypted` is metadata-prefix based. It avoids false positives for original-size-only old metadata, but broad prefix matches can still classify incomplete metadata as encrypted.
- Actual-size logic for compressed objects depends on metadata or part actual sizes. Missing part actual sizes on nonempty compressed objects return an error.
- Version listing marker behavior intentionally applies the version marker only to the first object entry; changing this would break pagination.
- `from_meta_cache_entries_sorted_*` suppresses parse errors by logging and continuing, which favors availability but can hide corrupt entries from callers.
- `Clone` shares `Arc` fields and drops `put_object_reader`; code expecting cloned upload streams would fail silently by seeing `None`.
- `decrypt_checksums` still has a TODO for encrypted checksum handling and currently returns part checksums or raw object checksum metadata.

## Test Signals

Tests cover null and UUID version markers, one-time version-marker application across multiple entries, actual-size precedence and compressed metadata/part fallbacks, errors for compressed size mismatch, empty ETag precondition handling, preservation of replication decisions from `FileInfo`, encryption detection for old metadata and current RustFS/SSE metadata including case-insensitive keys, and `ObjectInfo::clone` behavior with shared `Arc` fields and omitted reader state.
