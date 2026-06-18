# sources/storage-engines/tikv/src/storage/raw/store.rs

## Purpose
This file implements the raw-storage read facade over snapshots for API V1, API V1 TTL, and API V2. It centralizes raw get, TTL get, forward/reverse scan, and checksum logic while selecting the right snapshot adapter for each API version.

## Important APIs, Types, and Functions
- `RawStore<S>` is an enum with `V1`, `V1Ttl`, and `V2` variants.
- `RawStore::new` selects plain snapshot, `RawEncodeSnapshot<ApiV1Ttl>`, or `RawEncodeSnapshot<RawMvccSnapshot<S>, ApiV2>`.
- `raw_get_key_value` dispatches point reads and records flow stats.
- `raw_get_key_ttl` is valid only for TTL-capable API versions; V1 panics.
- `forward_raw_scan` and `reverse_raw_scan` configure bounds and dispatch to the inner generic implementation.
- `raw_checksum_ranges` computes CRC64 xor checksum, key/value count, and total bytes across key ranges.
- `MAX_TIME_SLICE` and `MAX_BATCH_SIZE` bound cooperative scan work before `yatp::reschedule`.

## Control Flow
Public `RawStore` methods pattern-match on API version and delegate to `RawStoreInner`. Forward scans build upper bounds from the optional end key, seek, then collect up to `limit` pairs while periodically yielding after enough rows and elapsed time. Reverse scans similarly set lower bounds and use `reverse_seek`/`prev`. Checksum iterates ranges, decodes user keys, and updates `checksum_crc64_xor`.

## State and Persistence Behavior
The file is read-only. V1 uses the snapshot directly. V1 TTL stores encoded raw values and filters/decodes them through `RawEncodeSnapshot`. V2 stores timestamped raw MVCC keys, projects latest versions with `RawMvccSnapshot`, then decodes values with `RawEncodeSnapshot<ApiV2>`. Flow statistics are mutable output state.

## Dependencies and Integration Points
It integrates `api_version` formats, engine iterator options, protobuf `ApiVersion` and `KeyRange`, `Cursor`, `Statistics`, `checksum_crc64_xor`, and YATP cooperative scheduling. It is the main raw read path used by storage commands after a snapshot has been acquired.

## Risks
`raw_get_key_ttl` panics on non-TTL V1 callers instead of returning an error. Scan fairness depends on both row count and elapsed time. Bound correctness depends on encoded keys and `DATA_KEY_PREFIX_LEN`. Checksum decoding malformed data surfaces as operation errors.

## Test Signals
Direct tests are absent in this file. Coverage comes through raw API command tests and `raw_mvcc.rs` adapter tests. Important scenarios include API-version dispatch, TTL filtering, zero-limit scans, key-only scans, reverse bounds, cooperative rescheduling, and checksum parity.
