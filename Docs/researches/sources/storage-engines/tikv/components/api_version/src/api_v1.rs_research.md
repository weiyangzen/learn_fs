# sources/storage-engines/tikv/components/api_version/src/api_v1.rs

## Purpose
`api_v1.rs` implements the `KvFormat` contract for legacy API V1 raw KV. V1 stores raw keys and values without API-version-specific prefixes, TTL metadata, or delete metadata.

## Important APIs, Types, And Functions
- `impl KvFormat for ApiV1` sets `TAG = ApiVersion::V1`, `CLIENT_TAG = V1` in tests, and `IS_TTL_ENABLED = false`.
- `parse_key_mode` and `parse_range_mode` return `KeyMode::Unknown`.
- `decode_raw_value`, `encode_raw_value`, and `encode_raw_value_owned` pass user bytes through unchanged.
- `convert_raw_encoded_key_version_from` and `convert_raw_user_key_range_version_from` allow V1/V1ttl sources and reject V2 sources.

## Control Flow
All operations are direct pass-throughs except conversion, which matches on source API version. V2-to-V1 conversion is explicitly unsupported because V2 carries keyspace/prefix semantics that cannot be blindly dropped.

## State And Persistence Behavior
This defines the legacy persistent representation: raw key bytes are encoded keys, and raw value bytes are stored as user values. No TTL or deletion metadata is represented.

## Dependencies And Integration Points
It implements trait definitions from `lib.rs`, uses `txn_types::Key`, `kvproto::ApiVersion`, and `tikv_util::box_err` for conversion errors. It is dispatched through `dispatch_api_version!` throughout TiKV.

## Risks And Edge Cases
- V1 cannot infer raw/txn/TiDB mode from key prefixes.
- Conversions from V2 are rejected; callers must handle migration/backup compatibility explicitly.
- `RawValue.is_delete` and `expire_ts` are ignored by V1 encoding, so callers must not pass metadata expecting persistence.

## Test Signals
Tests in `lib.rs` cover V1 parse behavior, value encode/decode identity, raw key identity, value conversion involving V1, and rejection paths through dispatch macros.
