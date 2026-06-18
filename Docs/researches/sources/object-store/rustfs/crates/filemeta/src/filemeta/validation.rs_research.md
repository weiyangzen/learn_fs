# sources/object-store/rustfs/crates/filemeta/src/filemeta/validation.rs

Purpose: validation and statistics helpers for `FileMeta` and `FileMetaVersionHeader`.

Important APIs/types/functions: `FileMeta::is_compatible_with_meta`, `validate_integrity`, private `is_sorted_by_mod_time`, `get_version_stats`, `VersionStats`, `FileMetaVersionHeader::is_valid`, `DetailedVersionStats`, and `FileMeta::get_detailed_version_stats`.

Control flow: integrity validation checks newest-first ordering and delegates inline data validation. Basic compatibility currently requires `meta_ver == XL_META_VERSION`. Version stats count object versions, delete markers, invalid/legacy versions, and free versions. Header validation checks valid version type, allows mod times no more than 24 hours in the future, and validates erasure coding only when both erasure fields indicate EC is present. Detailed stats decode object version metadata to aggregate total object size and count data-dir/inline-data usage.

State and persistence: read-only validation over the in-memory representation loaded from persisted `xl.meta`. Future-time validation depends on current UTC time, so results can vary with clock skew.

Dependencies and integration: depends on `FileMetaVersion`, `VersionType`, `OffsetDateTime`, `time::Duration`, and inline-data validation. Benchmarks and unit tests call these helpers as compatibility and performance signals.

Risks: `is_compatible_with_meta` is intentionally minimal and does not validate header version or version body compatibility. Legacy versions are counted as invalid in `VersionStats` but separately in `DetailedVersionStats`, so consumers must choose the right stats type. Header EC validation is skipped if `has_ec` is false, allowing partial zero EC fields.

Test signals: filemeta tests and Criterion benchmarks cover integrity success, sorting expectations, version stats accuracy, detailed stats, header validation edge cases, and validation performance.
