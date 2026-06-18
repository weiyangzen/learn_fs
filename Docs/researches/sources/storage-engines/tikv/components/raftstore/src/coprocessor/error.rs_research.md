# sources/storage-engines/tikv/components/raftstore/src/coprocessor/error.rs

## Purpose
`error.rs` defines the small error surface used by raftstore coprocessor hooks and split-check helpers.

## Important APIs, Types, And Functions
`Error` has two variants: `RequireDelay { after, reason }`, for retry-after style coprocessor failures, and `Other(Box<dyn StdError + Sync + Send>)`, for boxed underlying errors. `Result<T>` aliases `StdResult<T, Error>`. `ErrorCodeExt` maps all variants to `error_code::raftstore::COPROCESSOR`.

## Control Flow
Most coprocessor modules return this `Result` and use `box_try!` or `box_err!` to convert lower-level failures into `Error::Other`. Dispatcher hooks that return `Result` short-circuit when this error is produced.

## State And Persistence Behavior
No state is stored or persisted. The only operational behavior is classification of errors for observability and error-code propagation.

## Dependencies And Integration Points
Depends on `thiserror`, `error_code`, and standard error traits. It is re-exported from `coprocessor/mod.rs` and used across dispatcher, split-check, and region-info provider methods.

## Risks
`RequireDelay` is defined here but not handled specially in the files in this subset; upstream callers need to preserve the retry semantics. The broad boxed `Other` type keeps conversion easy but can hide structured failure details unless logs include source errors and codes.

## Test Signals
No direct tests in this file. Coverage is indirect through modules that return `coprocessor::Result`, especially split-check approximate-stat tests and dispatcher error short-circuit tests.
