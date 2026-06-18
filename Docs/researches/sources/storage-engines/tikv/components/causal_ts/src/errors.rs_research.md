# sources/storage-engines/tikv/components/causal_ts/src/errors.rs

## Purpose
Defines causal timestamp provider error types and maps them to TiKV error codes.

## APIs, Types, And Functions
`Error` variants are `Pd`, `Tso`, `TsoBatchUsedUp`, `BatchRenew`, and `Other`. `Result<T>` aliases the crate result type. `ErrorCodeExt` maps variants to `error_code::causal_ts` codes or `UNKNOWN`.

## Control Flow
Provider code uses `?` conversions from PD errors and boxed errors. Batch renew failures wrap shared error objects in `Arc` so coalesced request waiters can receive cloned results.

## State And Persistence
Errors carry no persistent state, but their codes become externally visible through TiKV error handling and logging.

## Dependencies And Integration Points
Integrates with `pd_client`, `error_code`, `thiserror`, and the rest of the causal_ts crate.

## Risks And Test Signals
Precise error classification matters for diagnostics. `TsoBatchUsedUp` includes the last batch size, which helps identify under-renew or PD failure conditions.
