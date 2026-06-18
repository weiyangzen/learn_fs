<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/serde_datetime.rs -->
# sources/object-store/rustfs/crates/credentials/src/serde_datetime.rs

## Purpose
Provides serde helpers for optional credential expiration timestamps, writing RFC3339 and reading either RFC3339 or legacy RustFS human-readable format.

## Important APIs, types, and functions
`legacy_format()` lazily parses and caches an owned time format. `parse_rfc3339_or_legacy` tries well-known RFC3339 first, then legacy. `option::serialize` serializes `Option<OffsetDateTime>` as RFC3339 or null; `option::deserialize` accepts optional strings and parses through the fallback helper.

## Control flow
Deserialization reads `Option<&str>`, returns `Ok(None)` for missing/null, and maps parse errors to serde custom errors. The legacy format cache is initialized once through `OnceLock`.

## State and persistence behavior
State is limited to the process-global parsed legacy format. Serialized timestamps persist in JSON credentials.

## Dependencies and integration points
Integrated by `Credentials.expiration` through `#[serde(default, with = "crate::serde_datetime::option")]` and depends on the `time` crate.

## Risks and edge cases
Legacy parsing widens accepted input and should remain compatible, but malformed strings fail deserialization for the whole credential. RFC3339 output can differ in fractional precision based on `time` formatting.

## Test signals
Credential tests verify RFC3339 serialization and MinIO-style RFC3339 deserialization. Additional tests should cover legacy format acceptance and invalid timestamp rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/serde_datetime.rs -->
