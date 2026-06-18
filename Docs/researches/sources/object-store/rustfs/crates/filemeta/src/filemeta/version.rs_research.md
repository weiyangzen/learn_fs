# sources/object-store/rustfs/crates/filemeta/src/filemeta/version.rs

## Purpose

This module owns version-level XL metadata parsing, encoding, conversion to `FileInfo`, and compatibility with older RustFS/MinIO metadata layouts. It is the main bridge between raw msgpack bytes stored in `xl.meta`, shallow version headers used for list/merge operations, full object/delete-marker metadata, legacy v1/v2 metadata, replication transition metadata, inline-data flags, and high-level object information returned to storage callers.

The file starts with an explicit rule: callers must parse version bytes through `FileMetaShallowVersion::parse_version_meta`, `FileMetaShallowVersion::into_fileinfo`, or `FileMetaVersion::try_from(&[u8])`. Direct `default()` plus `unmarshal_msg()` is intentionally discouraged because it skips the legacy `rmp_serde` fallback path.

## Important APIs, Types, and Functions

- `FileMetaShallowVersion` stores a `FileMetaVersionHeader` plus serialized full version bytes. `parse_version_meta()` delegates to `FileMetaVersion::try_from`, `into_fileinfo()` parses then converts, and `TryFrom<FileMetaVersion>` builds shallow entries by deriving a header and marshaling the full version.
- `FileMetaVersion` represents one version. It carries `version_type`, optional `MetaObjectV1`, optional current `MetaObject`, optional `MetaDeleteMarker`, `write_version`, and `uses_legacy_checksum`.
- `FileMetaVersion::try_from(&[u8])` is the central decoder. It first tries handwritten msgpack decoding and validates the result. If that fails, it tries the explicit `LegacyMetaV2Version` serde shape, then falls back to serde-decoding `FileMetaVersion` itself, marking legacy checksum behavior.
- `FileMetaVersion::decode_data_dir_from_meta()` optimizes extraction of `DDir` from a V2 object by scanning only enough msgpack to find `Type` and `V2Obj`, then falls back to full decode.
- `FileMetaVersionHeader` is the sortable, compact version identity. It stores version id, mod time, signature, version type, flags, and erasure data/parity counts. It has legacy header readers `unmarshal_v1`, `unmarshal_v2`, current `unmarshal_msg`, and `matches_not_strict`/`matches_ec` helpers for quorum merge.
- `MetaObject` is the current object metadata shape with custom msgpack field names such as `ID`, `DDir`, `EcAlgo`, `PartNums`, `MTime`, `MetaSys`, and `MetaUsr`.
- `MetaObjectV1` plus nested `MetaObjectV1Stat`, `MetaObjectV1Erasure`, `MetaObjectV1ChecksumInfo`, and `MetaObjectV1Part` model the older V1 object body and convert it to modern `FileInfo`, `ErasureInfo`, `ChecksumInfo`, and `ObjectPartInfo`.
- `MetaDeleteMarker` represents delete markers and tier free-version delete entries, including free-version transition metadata.
- `VersionType`, `ChecksumAlgo`, and `Flags` encode stored enum values and header flags.
- `merge_file_meta_versions()` merges per-disk shallow-version streams under quorum, strict/non-strict matching, requested version limits, version id de-duplication, and free-version accounting.
- `file_info_from_raw()` and `get_file_info()` are public raw-buffer entry points that load `FileMeta`, select a version, and return `FileInfo`.
- `read_xl_meta_no_data()` asynchronously reads only the metadata portion of an XL file, accounting for metadata header versions and CRC trailer sizing.

## Control Flow

Decode flow starts with msgpack helper functions for strings, binary blobs, and timestamp ext types. Current-format `FileMetaVersion::decode_from()` reads a msgpack map, resets to default, dispatches on keys, instantiates nested `MetaObject` or `MetaDeleteMarker` through `PrependByteReader` when a non-nil marker was already consumed, and skips unknown fields for forward compatibility.

If current decode is invalid, the `TryFrom<&[u8]>` path tries legacy serde shapes. `LegacyMetaV2Version` is normalized into current `FileMetaVersion` by converting object/delete-marker UUID byte fields, erasure/checksum algorithm strings, vectors, mod times, and metadata maps. A final serde fallback supports older named-field layouts.

Encoding flow is custom and intentionally not generic serde: `FileMetaVersion::encode_to()` writes a compact variable-size map, `MetaObject::encode_to()` writes Go-compatible names and omits/nils specific optional arrays/maps, and `MetaDeleteMarker::encode_to()` writes its fixed three-field map. Header encoding uses a seven-element array.

Conversion to `FileInfo` branches by version type. Object conversion optionally expands parts, filters user metadata, converts internal byte metadata to strings, extracts CRC/transition fields by suffix, reconstructs erasure info, builds replication state from internal metadata, and marks objects deleted when purge status is present. Delete marker conversion marks `deleted`, preserves metadata, reconstructs replication state, and for free-version markers populates transition tier/object/version id fields.

`merge_file_meta_versions()` repeatedly compares the top entry of each input stream, accepts identical tops, otherwise chooses the newest/preferred header according to strictness and non-strict matching, requires quorum, removes consumed/duplicate entries across streams, and appends remaining entries from the first stream when a requested non-free version count is reached.

`read_xl_meta_no_data()` reads an initial prefix, checks XL2 version, and for minor versions reads either the whole file, the declared metadata payload, or metadata plus enough CRC bytes to return only the no-data metadata prefix.

## State and Persistence Behavior

The persisted representation is msgpack-based and path-critical: object metadata is stored in `FileMetaShallowVersion.meta`, while a compact `FileMetaVersionHeader` is stored alongside it for indexing, sorting, and quorum decisions. Header versions 1, 2, and 3 are all read; current header v3 includes erasure counts and inline/data-dir/free-version flags. Object/delete metadata stores UUIDs as 16-byte binary values, nil UUIDs become `None` on decode in most full-object paths, and Unix epoch timestamps are normalized to absent mod times.

`MetaObject` separates `meta_user` from `meta_sys`. Internal metadata suffixes persist transition status, transitioned object name, transitioned version id, transition tier, CRC, inline data, tier free-version ids/markers, and replication/purge/reset status. `init_free_version()` can synthesize a persisted delete-marker entry with the free-version suffix and copied transition fields for tiered objects.

The module never writes external storage directly; persistence is through serialized byte buffers returned by `marshal_msg()` or by loading buffers into `FileMeta`.

## Dependencies and Integration Points

The module depends on the parent `filemeta` module for constants and `FileMeta`, on `fileinfo` types for `FileInfo`, erasure, part, and metadata constants, on `msgp_decode` for value skipping and nil-aware array/map readers, on `replication.rs` for replication state/status parsing, and on `rustfs_utils::http` for internal metadata suffix helpers. It also uses `rmp`, `rmp_serde`, `serde`, `uuid`, `time`, `bytes`, `tokio::io::AsyncRead`, `xxhash_rust`, and `tracing`.

External callers include raw metadata readers, metacache reconciliation, object listing/get-file-info paths, healing and erasure-store code that need data-dir/inline/free-version decisions, and tests/fixtures in `test_data.rs`.

## Risks and Edge Cases

- Parsing correctness is high risk because a bad decoder can make older `xl.meta` files unreadable. The fallback contract in `TryFrom<&[u8]>` is therefore critical.
- Several decode paths cast signed integers to `usize`/`u8` after reading `i64`; malformed negative values could wrap unless guarded by the specific field code. `write_version` explicitly rejects negative values, but many erasure/part fields do not.
- `MetaObject::into_fileinfo(all_parts=true)` indexes `part_sizes` and `part_actual_sizes` by `part_numbers.len()` without checking all vectors have the same length. Corrupt or legacy metadata with mismatched vectors could panic.
- `MetaDeleteMarker::decode_from()` errors on unknown fields, unlike object/version decode paths that skip unknowns. That is less forward-compatible for delete marker evolution.
- `init_free_version()` panics on invalid tier free-version id instead of returning an error.
- Header signatures derived by `From<FileMetaVersion> for FileMetaVersionHeader` are initialized to zero, while separate `get_signature` helpers compute content signatures. Callers relying on nonzero signatures need to update or derive them explicitly.
- The fast `decode_data_dir_from_v2_object()` depends on map field order enough to see `Type` before interpreting `V2Obj`; it falls back to full parsing on failure, which protects correctness but can cost work.
- `read_xl_meta_no_data()` has subtle length arithmetic around CRC sizing and partial reads; off-by-one or malformed length handling could lead to `FileCorrupt` or unexpected EOF.

## Test Signals

This file contains substantial unit tests. They verify v1/v2/v3 header decoding, legacy v1 object body conversion to `FileInfo`, legacy meta v2 delete marker decoding, invalid legacy UUID rejection, nil legacy UUID acceptance for object/delete marker paths, fast data-dir extraction, transition version id nil filtering, and free-version delete marker transition id handling. Fixture helpers in `test_data.rs` provide real/corrupt/legacy XL metadata used by other tests.
