# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mod.rs

## Purpose
Declares the public codec module tree and shared codec-level helpers. It exposes the main submodules for batch, chunk, collation, conversion, data types, datums, MySQL types, row/table codecs, overflow helpers, and common error/result exports.

## Important APIs, Types, And Functions
- `invalid_type!` macro: local shortcut for creating `Error::InvalidDataType` from a literal or formatted message.
- Public modules: `batch`, `chunk`, `collation`, `convert`, `data_type`, `datum`, `datum_codec`, `error`, `mysql`, `row`, and `table`.
- Private module: `overflow`, with selected public re-exports.
- Public re-exports: `Datum`, `Error`, `Result`, `div_i64`, `div_i64_with_u64`, and `div_u64_with_i64`.
- `TEN_POW`: shared powers-of-ten table from `10^0` through `10^9`.

## Control Flow
The file is mostly declarative. The macro expands at call sites to construct invalid-data errors. Module visibility controls which codec subsystems are part of the crate API, and re-exports provide stable short paths for common datum/error/overflow items.

## State And Persistence Behavior
No runtime state or persistence. The powers-of-ten table is a static constant used by numeric/time/decimal logic elsewhere in the codec package.

## Dependencies And Integration Points
This is the integration root for all codec users in `tidb_query_datatype`. Other modules import `crate::codec::{Error, Result, Datum}` or call `invalid_type!`. Row/table/index codec layers are exposed here for higher-level query components.

## Risks And Edge Cases
- `invalid_type!` is defined in this module and relied on by child modules; macro visibility/order matters.
- Public module exports form a compatibility surface for downstream crates.
- The TODO about replacing the old failure-style boxed error shortcut signals historical error handling that may still leak through `box_err!` uses.

## Test Signals
No local tests. Module-level correctness is covered by successful compilation and downstream tests for the exposed submodules.
