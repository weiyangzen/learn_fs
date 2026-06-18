<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/doc.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/doc.rs

Purpose: Defines a versioned persisted policy document wrapper that can carry create/update timestamps around a `Policy` while also accepting legacy bare policy JSON.

Important APIs/types/functions: `PolicyDoc` has `Version`/`version`, `Policy`/`policy`, `CreateDate`/`create_date`, and `UpdateDate`/`update_date` serde mappings. `PolicyDoc::new`, `update`, and `default_policy` construct or mutate wrappers. `TryFrom<Vec<u8>>` parses either a `PolicyDoc` or a bare `Policy`.

Control flow: `new` sets version `1` and both timestamps to now. `update` increments version, replaces policy, updates update date, and backfills create date if it was missing. `default_policy` creates version `1` without timestamps. The byte parser first attempts full document deserialization, then falls back to bare policy and wraps it; if both fail it emits a custom serde error.

State/persistence behavior: This is a persisted JSON compatibility boundary. It serializes with MinIO-style capitalized field names and RFC3339 option timestamps through crate datetime helpers while accepting legacy lowercase aliases.

Dependencies/integration: Uses serde, `time::OffsetDateTime`, `crate::serde_datetime::option`, and `Policy`. IAM policy storage/loading code can use it to preserve update metadata while remaining backward compatible.

Risks/test signals: If bare `Policy` parsing succeeds, wrapper metadata defaults to version `0` and no dates because `Default` is used. `TryFrom<Vec<u8>>` masks the detailed first/second parse errors with a generic custom error. Tests cover RFC3339 serialization, MinIO-style timestamp deserialization, and timestamp round-trip.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/doc.rs -->
