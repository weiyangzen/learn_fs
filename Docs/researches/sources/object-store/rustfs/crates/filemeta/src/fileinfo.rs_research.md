# sources/object-store/rustfs/crates/filemeta/src/fileinfo.rs

Purpose: public object metadata model used after decoding `xl.meta` and before storage/object APIs consume metadata.

Important APIs/types/functions: constants include `ERASURE_ALGORITHM`, `BLOCK_SIZE_V2`, `NULL_VERSION_ID`, and tier-free metadata keys. `ObjectPartInfo` models part number, sizes, ETag, optional compression index, checksums, and errors. `ChecksumInfo`, `ErasureAlgo`, and `ErasureInfo` model erasure coding and bitrot checksums, with `calc_shard_size`, `shard_size`, `shard_file_size`, `get_checksum_info`, and `equals`. `FileInfo` contains volume/object identity, version/delete status, transition/restore fields, data dir, mod time, size, metadata map, parts, erasure info, replication state, inline data, checksum, and legacy checksum marker. `FileInfoVersions`, `RawFileInfo`, and `FilesInfo` are aggregate DTOs. `RestoreStatusOps`, `parse_restore_obj_status`, and `is_restored_object_on_disk` handle S3 restore headers.

Control flow: `FileInfo::new` computes deterministic erasure distribution from a CRC32 of the object name. `is_valid` allows delete markers and validates data/parity/index/distribution for object entries. Part insertion replaces matching part numbers and sorts. Offset lookup walks parts cumulatively. Metadata helper methods set/read internal healing, inline-data, data-moved, tier-free, skip-tier-free, compression, and remote/tiering flags. Quorum helpers distinguish deleted objects from erasure-coded objects. Equality helpers compare compression, transition, mod time, erasure, metadata, and replication fields. Restore parsing validates `ongoing-request` and RFC3339 expiry syntax.

State and persistence: this module represents persisted object metadata after decoding and before encoding. Inline data and part indexes use `bytes::Bytes`; metadata flags use HTTP/internal suffix helpers. Restore on-disk state is derived from `x-amz-restore` expiry compared to current UTC time.

Dependencies and integration: uses `serde`, `rmp-serde`, `bytes`, `time`, `uuid`, `s3s` restore headers, `rustfs_utils` HTTP/hash helpers, and replication types from the crate. It is consumed by `FileMeta`, ecstore tests, object info conversion, tiering, healing, and replication flows.

Risks: restore header parser accepts a narrow format and only RFC3339 expiry, while `to_string2` emits RFC1123. `is_remote` depends on current time through restore status, making behavior time-sensitive. `FileInfo::new` distribution must remain compatible with MinIO/RustFS erasure layout. Metadata keys are plain strings; suffix helper behavior is critical to avoid persisting transient flags.

Test signals: direct tests are not in this file, but `filemeta.rs`, examples, and MinIO fixture tests exercise FileInfo construction, erasure layout, inline data, restore/tiering behavior, parts, and metadata extraction.
