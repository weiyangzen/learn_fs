# sources/object-store/rustfs/crates/filemeta/src/test_data.rs

## Purpose

This module builds deterministic and fixture-backed `xl.meta` byte buffers for tests. It covers current metadata, complex multi-version metadata, inline-data metadata, corrupted metadata, empty metadata, hand-built legacy v1 metadata, and real legacy hex fixtures captured from RustFS issues.

## Important APIs, Types, and Functions

- `create_real_xlmeta()` builds a `FileMeta` with one object version, one delete marker, and one manually adjusted legacy shallow version, then sorts by newest mod time and marshals it.
- `create_issue_2288_legacy_xlmeta()`, `create_issue_2265_legacy_meta_v2_object_xlmeta()`, `create_issue_2265_legacy_meta_v2_config_xlmeta()`, and `create_issue_2434_legacy_meta_v2_pool_xlmeta()` decode included hex fixtures.
- `create_legacy_v1_object_xlmeta()` hand-builds an XL2 file with legacy v1 header/body layout and CRC.
- `create_complex_xlmeta()` creates ten object versions plus periodic delete markers with varying UUIDs, data dirs, sizes, etags, and times.
- `create_corrupted_xlmeta()` returns a deliberately truncated XL2 payload.
- `create_empty_xlmeta()` marshals an empty `FileMeta`.
- `verify_parsed_metadata()` asserts version count, metadata version, and descending mod-time ordering.
- `create_xlmeta_with_inline_data()` stores inline payload bytes in `FileMeta.data` and adds one object version referencing the inline version id.

## Control Flow

The builder functions construct `MetaObject`, `MetaDeleteMarker`, and `FileMetaVersion` values, convert them to `FileMetaShallowVersion`, push them into `FileMeta.versions`, sort when needed, and call `FileMeta::marshal_msg()`. Legacy helpers manually encode msgpack headers and bodies with `rmp`, write the XL2 magic/version bytes, patch the data length into the header, and append an xxh64 CRC trailer.

The fixture helpers call `decode_hex_fixture()`, which trims the included fixture string, validates even length, converts each hex pair with `to_digit(16)`, and returns bytes or a crate error naming the invalid index.

## State and Persistence Behavior

All state produced is in-memory byte vectors, but those vectors are intended to match persisted `xl.meta` layouts. The real fixture functions use `include_str!("../tests/fixtures/...")`, tying the compiled crate to fixture files under `crates/filemeta/tests/fixtures`. Legacy hand-built data writes `"XL2 "`, little-endian header/meta versions, a msgpack bin32 length marker, msgpack metadata body, and a big-endian CRC marker/value.

## Dependencies and Integration Points

This module depends on crate-local metadata types, `time::OffsetDateTime`, `uuid`, `xxhash_rust`, `rmp`, and fixture files. It is exported as `pub mod test_data` by `lib.rs` and is used by unit tests in `metacache.rs`, likely by `filemeta` tests, and by downstream crates that need realistic metadata bytes.

## Risks and Edge Cases

- Several helpers use `Uuid::new_v4()` and `OffsetDateTime::now_utc()`, so some generated metadata is nondeterministic. Tests should assert structural properties rather than exact bytes for those helpers.
- The public `verify_parsed_metadata()` uses assertions rather than returning normal validation errors for mismatches; it can panic in callers.
- `create_real_xlmeta()` includes a `VersionType::Legacy` shallow version with no `legacy_object` body and manually adjusted header fields. It is useful for ordering/header tests but not a fully valid legacy object body.
- The hand-built legacy XL2 writer has low-level length/CRC logic; changes to `FileMeta` wire format can silently stale this fixture builder.
- Fixture include paths must remain valid for crate compilation.

## Test Signals

Local tests verify that real, complex, inline-data, corrupted, and empty metadata helpers produce parseable or intentionally failing buffers. They assert XL2 magic, version counts, inline data presence, and corrupted-load failure.
