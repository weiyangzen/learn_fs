# sources/object-store/rustfs/crates/ecstore/src/bucket/metadata.rs

Purpose: Defines the persisted bucket metadata record, its MessagePack wire format, compatibility decoders, config byte fields, parsed config caches, and disk load/save functions. This is the central persistence contract for bucket policy, lifecycle, notification, object lock, versioning, encryption, tagging, quota, replication, target, CORS, logging, website, accelerate, request-payment, public-access-block, ACL, and table-bucket state.

Important APIs and types: `BucketMetadata` stores raw config bytes, updated-at timestamps, and parsed `Option<T>` caches. `decode_from` and `encode_to` implement a MinIO-compatible map format behind a 4-byte little-endian format/version header. `marshal_msg`, `unmarshal`, and `check_header` wrap codec operations. `update_config` routes known config filenames to the correct byte field and timestamp. `save` parses configs, writes the header and MessagePack body, and persists to `.buckets/<bucket>/.metadata.bin`. `load_bucket_metadata`, `load_bucket_metadata_parse`, and `read_bucket_metadata` read from the object store and optionally parse.

Control flow and state: Unknown MessagePack fields are skipped via `msgp_decode::skip_msgp_value`, preserving forward compatibility. Legacy times can be ext8, compact arrays, nil, or bin-wrapped values; legacy byte arrays and numeric booleans are accepted. `default_timestamps` backfills missing updated-at values from creation time. `parse_all_configs` logs per-config parse warnings and continues, so raw bytes can be retained even when a parsed cache is invalid.

Dependencies and integration: Uses `read_config`/`save_config`, `resolve_object_store_handle`, S3 DTO config types, `rustfs_policy::BucketPolicy`, quota and target modules, `ObjectLockApi`, `VersioningApi`, and SHA-256 helpers for table-bucket catalog paths.

Risks: `encode_to` hardcodes a map length of 41; adding fields requires synchronized updates. `parse_all_configs` can leave stale parsed `Option` values if a later invalid non-empty config is parsed on an already-populated struct. Save requires a global object store handle, limiting isolated tests. Table-bucket presence is a byte-marker check.

Test signals: Tests cover round-trip serialization, complete metadata examples, table-bucket marker toggling, and clearing cached policy state. `metadata_test.rs` adds broader compatibility coverage for legacy formats.
