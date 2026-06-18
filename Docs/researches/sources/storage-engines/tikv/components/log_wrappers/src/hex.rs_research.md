# sources/storage-engines/tikv/components/log_wrappers/src/hex.rs

## Purpose
This file re-exports selected functions from the `hex` crate for the `log_wrappers` API.

## Important APIs, Types, and Functions
It publicly re-exports `hex::encode` as `hex_encode` and `hex::encode_upper` as `hex_encode_upper`.

## Control Flow
No local control flow; calls dispatch to the external `hex` crate.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
`log_wrappers::Value` uses `hex_encode_upper` to print keys and values consistently. Other crates can import these helpers through `log_wrappers`.

## Risks
The wrapper fixes naming and casing expectations. Replacing uppercase encoding would change log output and tests.

## Test Signals
The behavior is indirectly tested by `test_log_key` and redaction tests in `src/lib.rs`.
