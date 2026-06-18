# sources/storage-engines/tikv/components/api_version/src/api_v2.rs

## Purpose
`api_v2.rs` implements API V2 key/value format. V2 separates raw, transactional, and TiDB-compatible key modes by prefixes, reserves a 3-byte keyspace id, memcomparable-encodes raw keys, optionally appends timestamps, and stores value metadata flags for TTL and logical deletion.

## Important APIs, Types, And Functions
- Prefix constants: raw `b'r'`, txn `b'x'`, TiDB meta `b'm'`, TiDB table `b't'`, default keyspace `[0,0,0]`, and default keyspace end `[0,0,1]`.
- `TIDB_RANGES` and `TIDB_RANGES_COMPLEMENT` describe TiDB-compatible key ranges.
- `ValueMeta` bitflags define `EXPIRE_TS` and `DELETE_FLAG`.
- `impl KvFormat for ApiV2` implements mode parsing, raw value encode/decode, raw key encode/decode, and V1/V1ttl-to-V2 conversion.
- `ApiV2::append_ts_on_encoded_bytes`, `decode_ts_from`, `split_ts`, `add_prefix`, `get_rawkv_range`, and `ENCODED_LOGICAL_DELETE` are helper APIs.

## Control Flow
Key-mode parsing reads the first byte. Range-mode parsing only succeeds when bounded start/end share a mode prefix or use the special exclusive end of `prefix + 1`. Value decoding removes the final flag byte, optionally removes an 8-byte expire timestamp, and returns delete/TTL metadata. Raw key encoding memcomparable-encodes the user key and optionally appends a descending timestamp. Conversion from V1/V1ttl adds raw prefix plus default keyspace before encoding.

## State And Persistence Behavior
V2 persistent keys are memcomparable encoded and can carry MVCC-like raw timestamps. Timestamp zero is invalid for raw MVCC because such entries cannot be retrieved correctly. V2 values always end in a metadata byte; TTL and logical deletion are durable flags.

## Dependencies And Integration Points
This file depends on `codec::byte::MemComparableByteCodec`, TiKV byte/number codecs, `txn_types::Key` and `TimeStamp`, shared `KvFormat`, and API-version dispatch. It is integrated by backup, GC worker, server storage, coprocessor, config validation, and keyspace parsing.

## Risks And Edge Cases
- Several validity checks are `debug_assert!`; invalid encoded keys can panic in tests but may rely on upstream validation in release builds.
- API V2 range parsing returns `Unknown` for unbounded or cross-prefix ranges, requiring callers to split ranges correctly.
- Conversion from V1 empty end key maps to default keyspace end; mistakes here can leak across keyspace boundaries.
- Logical deletion is represented as an encoded one-byte value `[DELETE_FLAG]`, so consumers must decode values rather than compare raw bytes casually.

## Test Signals
Inline tests cover invalid key decoding, invalid timestamp append, timestamp splitting, timestamp decoding, append-ts behavior, and logical delete encoding. `lib.rs` adds parse, range, raw key/value identity, conversion, TTL, metadata, and decode-error coverage.
