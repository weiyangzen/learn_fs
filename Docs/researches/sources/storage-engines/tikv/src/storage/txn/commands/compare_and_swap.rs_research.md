# sources/storage-engines/tikv/src/storage/txn/commands/compare_and_swap.rs

## Purpose
Implements raw compare-and-swap for raw KV. It reads the current raw value, compares it with an expected value, and conditionally writes a new value or deletes the key while always returning the previous value and success flag.

## Important APIs, Types, and Functions
`RawCompareAndSwap` fields include CF, key, expected value, replacement value, TTL, API version, and delete flag. It uses `RawStore::raw_get_key_value` for reads, `RawValue` encoding for writes, `ttl_to_expire_ts`, and API-version templates for value encoding. `ProcessResult::RawCompareAndSwapRes` carries the result.

## Control Flow
`process_write` reads the old value from the snapshot. If it matches `previous_value`, delete mode writes a delete only when a value exists; API V2 represents delete as an encoded logical-delete put. Put mode encodes the new raw value with TTL and writes it. API V2 raw timestamps from `raw_ext` are appended to the key before mutation. If comparison fails, no writes or guards are returned.

## State and Persistence
Successful puts or non-noop deletes produce one `Modify`; successful delete of a missing key is a no-op with success. Writes are allowed on disk-almost-full. Raw API timestamp key guards are returned when a timestamped mutation is produced. Response policy is `OnApplied`.

## Dependencies and Integration Points
Depends on raw storage format traits, raw TTL encoding, causal timestamp provider through `get_raw_ext`, and the common scheduler write path. It is dispatched by `Command::RawCompareAndSwap`.

## Risks and Test Signals
Risks include API V1/V2 behavioral divergence, delete-on-missing semantics, logical delete encoding, and stale value comparison when raw timestamp reads are involved. Tests cover nil/value compares, put, delete, TTL encoding, API-version templates, fail/no-op cases, and API V2 key guards.
