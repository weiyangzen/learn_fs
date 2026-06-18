# sources/object-store/rustfs/crates/utils/src/obj/metadata.rs

## Purpose
Extracts user-defined object metadata from a larger metadata map by removing system, S3, RustFS, and MinIO internal keys.

## Important APIs, Types, And Functions
`extract_user_defined_metadata` takes `&HashMap<String, String>` and returns a new map. It excludes standard headers such as content type, cache control, length, MD5, date, ETag, and last-modified; skips internal RustFS/MinIO metadata via `is_internal_key`; strips `x-amz-meta-` and `x-rustfs-meta-` prefixes into user keys; skips other `x-amz-*`, `x-rustfs-*`, and `x-minio-*` headers; and preserves all other keys as user-defined.

## Control Flow And State
The function is a single pass with a fresh output map. It lowercases keys for classification and inserts stripped user-metadata keys in lowercase, while unprefixed user keys retain their original spelling.

## Dependencies And Integration Points
Imports HTTP classification helpers from `crate::http`, so it depends on HTTP feature availability within the `obj` feature configuration. It is re-exported by `obj/mod.rs` and used wherever object metadata must be shown or propagated without system internals.

## Risks And Test Signals
Lowercasing prefixed user metadata can change key spelling, and collisions can overwrite values when differently cased/prefixed keys normalize to the same user key. The doc note correctly warns returned keys may differ from input keys. Tests cover system-header exclusion, AMZ/RustFS prefix stripping, MinIO exclusion, mixed cases, empty input, and case-insensitive filtering.
