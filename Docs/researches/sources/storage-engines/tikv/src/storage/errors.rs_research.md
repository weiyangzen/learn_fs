# sources/storage-engines/tikv/src/storage/errors.rs

## Purpose

This module centralizes storage-layer error representation and conversion to TiKV client-facing protobuf errors, error codes, metrics tags, and shared error handles.

## Important APIs, Types, And Functions

`ErrorInner` enumerates storage errors, wrapping KV, transaction, engine, IO, closed, busy, key-size, CF, TTL, deadline, API-version, and key-mode cases. `Error` is a boxed wrapper around `ErrorInner` with broad `From` conversions. `ErrorCodeExt` maps storage errors to structured TiKV error codes. `ErrorHeaderKind` classifies region-header protobuf errors and provides metric strings.

Conversion helpers include `get_error_kind_from_header`, `get_tag_from_header`, `extract_region_error_from_error`, `extract_region_error`, `extract_committed`, `extract_key_error`, `extract_kv_pairs`, `map_kv_pairs`, `map_kv_pair_entries`, and `extract_key_errors`. `SharedError` wraps `Arc<Error>` for sharing non-cloneable errors and can be converted back to owned `Error` only when uniquely referenced.

## Control Flow

Region error extraction pattern-matches nested storage/KV/transaction/MVCC errors to recover raftstore request headers, max timestamp not synced, flashback not prepared, invalid max-ts update, scheduler busy, GC busy, closed, and deadline exceeded cases. Key error extraction maps lock, conflict, already-exist, lock-not-found, transaction-not-found, deadlock, commit-ts-expired, commit-ts-too-large, assertion failed, and primary mismatch errors into `kvrpcpb::KeyError`; unknown cases become abort strings.

MVCC debug info for selected key errors is attached by `add_debug_mvcc_for_key_error`, which removes default-CF values before embedding to reduce response size. Pair mapping functions convert nested per-key `Result` values into protobuf pairs with per-entry errors where needed.

## State And Persistence Behavior

There is no persisted state. The module constructs protobuf error values and shared error wrappers. `SharedError` uses reference counting to allow one error to be passed to multiple waiters or responses.

## Dependencies And Integration Points

This file integrates error-code definitions, `kvproto` error and kvrpc protobufs, storage KV/MVCC/transaction errors, deadline utilities, transaction timestamp/key/value types, and storage command kinds. It is a key boundary between internal execution failures and client protocol responses.

## Risks And Edge Cases

The nested pattern matches are precise and can miss new error variants unless updated. Some conversions include formatted debug strings for compatibility, which may be relied on by older clients. `SharedError::try_from` fails if multiple references remain; callers that require owned errors must ensure uniqueness. Debug MVCC info intentionally strips values, which is good for response size but means diagnostics are incomplete.

## Test Signals

Tests cover write-conflict key-error conversion, transaction-lock-not-found conversion with and without MVCC debug info, and commit-ts-expired conversion with and without MVCC debug info.
