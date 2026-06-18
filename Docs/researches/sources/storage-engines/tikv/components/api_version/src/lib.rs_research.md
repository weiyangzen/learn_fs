# sources/storage-engines/tikv/components/api_version/src/lib.rs

## Purpose
`lib.rs` defines the public API-version abstraction for TiKV key/value formats. It exposes concrete marker types, the `KvFormat` trait, dispatch/test macros, key-mode classification, and the shared `RawValue` metadata struct.

## Important APIs, Types, And Functions
- Modules: private `api_v1`, `api_v1ttl`; public `api_v2` and `keyspace`.
- `KvFormat` defines version tag constants, key/range mode parsing, raw value encode/decode, raw key encode/decode, cross-version key/range/value conversion, and default V1-style key behavior.
- Marker structs: `ApiV1`, `ApiV1Ttl`, `ApiV2`.
- Macros: `test_kv_format_impl!`, `match_template_api_version!`, and `dispatch_api_version!`.
- `KeyMode` distinguishes Raw, Txn, Tidb, and Unknown.
- `RawValue<T>` carries user value, optional expiration timestamp, and logical delete flag, with `is_valid` and `is_ttl_expired` helpers.

## Control Flow
Callers usually dispatch from a runtime `kvproto::ApiVersion` to a concrete zero-sized type with `dispatch_api_version!`, then call trait methods statically. Default raw key methods are V1/V1TTL pass-throughs; API V2 overrides them. `convert_raw_encoded_value_version_from` decodes with the source API and re-encodes with the destination API.

## State And Persistence Behavior
This crate defines durable key/value encodings. `RawValue` validity combines logical deletion and TTL expiration. API V1 stores plain values, V1TTL stores an appended expiration timestamp, and V2 stores metadata flags plus optional TTL and delete state.

## Dependencies And Integration Points
The crate integrates with `kvproto::kvrpcpb::ApiVersion`, `txn_types::Key/TimeStamp`, `engine_traits::Result`, keyspace support, and `match-template` macro expansion. It is a foundational dependency for storage, backup/restore, GC, coprocessor, server, config validation, and tests.

## Risks And Edge Cases
- Persistent-format compatibility depends on the trait implementations remaining stable.
- `RawValue::is_valid` uses bitwise `&` on booleans; result is correct but both sides always evaluate.
- Dispatch macros generate match arms over known API versions; adding a new version requires updating macro templates and tests.
- V2 conversions are asymmetric: V1/V1TTL can convert to V2 for raw data, while V2-to-V1 key conversion is rejected in V1 files.

## Test Signals
This file has broad tests for parse behavior, range mode inference, value encoding across all versions, TTL and delete metadata, decode errors, validity checks, raw key encoding/decoding, raw key conversion to V2, raw value conversion among versions, and raw user-key range conversion.
