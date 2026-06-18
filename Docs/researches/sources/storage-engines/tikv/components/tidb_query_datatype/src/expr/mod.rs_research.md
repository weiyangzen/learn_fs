# sources/storage-engines/tikv/components/tidb_query_datatype/src/expr/mod.rs

## Purpose
This facade exposes expression evaluation context types and re-exports codec `Error`/`Result` for expression-facing users.

## Important APIs, types, and functions
It declares `mod ctx`, publicly re-exports everything from `ctx`, and re-exports `crate::codec::{Error, Result}`.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state is stored here. Stateful behavior lives in `ctx.rs`.

## Dependencies and integration points
This module lets other crates import `tidb_query_datatype::expr::{EvalContext, EvalConfig, Error, Result}` from one place. It is used by expression builders, codec conversions, and executors.

## Risks and edge cases
The module couples expression errors to codec errors by re-exporting the codec error type. That keeps old APIs simple but means expression and codec error domains are not cleanly separated.

## Test signals
There are no direct tests; coverage comes from `ctx.rs` and downstream expression/executor tests.
