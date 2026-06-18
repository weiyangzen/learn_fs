# sources/storage-engines/tikv/components/test_coprocessor/src/util.rs

## Purpose
This file contains general coprocessor test utilities: a global test ID generator, synchronous wrappers around coprocessor endpoint handling, result protobuf decoding, streaming response collection, and column-offset lookup.

## Important APIs And Functions
`next_id` increments an `AtomicUsize` with relaxed ordering and returns an `i64`. `handle_request` blocks on `Endpoint::parse_and_handle_unary_request` and consumes the response. `handle_select` decodes the response data into `tipb::SelectResponse`. `handle_streaming_select` maps streaming endpoint responses into `tipb::StreamResponse`s while allowing a caller-provided range check. `offset_for_column` returns the index of a column ID in a `ColumnInfo` slice.

## Control Flow And State
The utilities convert asynchronous coprocessor APIs into blocking test APIs. Streaming requests are collected fully before returning, so tests can inspect the complete response vector. The ID generator is process-global across the crate and intentionally simple.

## Dependencies And Integration Points
The file integrates `tikv::coprocessor::Endpoint`, TiKV `Engine`, `kvproto::coprocessor`, protobuf message decoding, futures executors/streams, and `tipb` response types.

## Risks And Test Signals
`handle_select` and streaming decoding assert non-empty response data and unwrap protobuf merges; error responses must be tested through lower-level APIs if needed. `offset_for_column` returns `0` when a column is not found, which can mask schema mistakes by targeting the first column. Because `next_id` uses relaxed ordering, it guarantees uniqueness but not synchronization semantics, which is sufficient for these tests.
