# sources/storage-engines/tikv/components/api_version/src/api_v1ttl.rs

## Purpose
`api_v1ttl.rs` implements `KvFormat` for API V1 with RawKV TTL. It preserves V1 key layout but appends an 8-byte expiration timestamp to every raw value.

## Important APIs, Types, And Functions
- `impl KvFormat for ApiV1Ttl` sets `TAG = V1ttl`, test `CLIENT_TAG = V1`, and `IS_TTL_ENABLED = true`.
- `parse_key_mode` and `parse_range_mode` always return `KeyMode::Raw` because txnkv is disabled in V1TTL.
- `decode_raw_value` splits the last 8 bytes as big-endian/u64 codec TTL, mapping zero to `None`.
- `encode_raw_value` and `encode_raw_value_owned` append `expire_ts.unwrap_or(0)`.
- Key and range conversion allows V1/V1ttl sources and rejects V2.

## Control Flow
Decoding validates that at least 8 bytes exist, decodes the TTL suffix, and returns the prefix as the user value. Encoding reserves/appends exactly one u64. Owned encoding mutates the user buffer to reduce allocation.

## State And Persistence Behavior
Values persist as `user_value || expire_ts_u64`; expiration timestamp zero represents no TTL. Delete metadata is not persisted in this format.

## Dependencies And Integration Points
The implementation uses TiKV codec number helpers, `engine_traits::Result`, `tikv_util::box_err`, and the shared `KvFormat`/`RawValue` types. It is used where storage config enables API V1 TTL compatibility.

## Risks And Edge Cases
- Any stored value shorter than 8 bytes is invalid in V1TTL.
- A caller setting `is_delete` loses that flag on encode.
- V2 conversion rejection must be surfaced by backup/import or migration callers.

## Test Signals
`lib.rs` tests cover V1TTL parse mode, no-meta and TTL value encoding, decode errors for too-short values, raw key identity, and value conversions to/from other versions.
