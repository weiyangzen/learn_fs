# sources/storage-engines/tikv/components/api_version/src/keyspace.rs

## Purpose
`keyspace.rs` adds keyspace-aware KV entry handling on top of API-version formats. V1/V1TTL have no keyspace prefix; API V2 parses a 3-byte keyspace id following the mode prefix and exposes user keys without that prefix.

## Important APIs, Types, And Functions
- `KvPairEntry` abstracts key/value/optional commit-ts access and provides `kv()`.
- `Keyspace` trait defines `make_kv_pair` and `parse_keyspace`.
- `KeyspaceId(u32)` wraps parsed keyspace identifiers.
- V1 and V1TTL `Keyspace` impls pass entries through and return `(None, key)`.
- V2 `Keyspace` impl returns `KeyspaceKv`, requiring valid raw or txn V2 keys with at least 4 prefix bytes.
- `KeyspaceKv` stores full encoded key, value, commit timestamp, and keyspace id while exposing `key()` without the first four bytes.

## Control Flow
`ApiV2::parse_keyspace` first delegates to `ApiV2::parse_key_mode`; only raw and txn keys are accepted. It rejects too-short or non-V2 data keys, builds a u32 from the 3 keyspace bytes, and returns the remaining user key slice. `make_kv_pair` parses the keyspace and stores it alongside the original tuple.

## State And Persistence Behavior
For V2, keyspace is persisted in the first four bytes of the data key: one mode byte plus three id bytes. `KeyspaceKv` preserves the original full key internally but hides the keyspace prefix from `KvPairEntry::key`.

## Dependencies And Integration Points
The module depends on `engine_traits::Result/Error`, `tikv_util::box_err`, `log_wrappers`, and API-version types. It is used by coprocessor/checksum/analyze and other components that need keyspace-stripped iteration while retaining keyspace identity.

## Risks And Edge Cases
- `ApiV2::make_kv_pair` unwraps `keyspace` after parse, relying on V2 parse always returning `Some`.
- `KeyspaceKv` equality against tuple compares exposed key/value/commit-ts, while equality against another `KeyspaceKv` compares full keys; this distinction is intentional but easy to misunderstand.
- Only raw and txn V2 keys are accepted; TiDB mode keys return errors for keyspace parsing.

## Test Signals
Unit tests cover V1/V1TTL no-keyspace behavior, valid V2 keyspace parsing for raw and txn prefixes, multi-byte ids, and error cases for missing/invalid prefixes or too-short keys.
