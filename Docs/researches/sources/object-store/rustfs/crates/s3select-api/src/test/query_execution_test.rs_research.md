# sources/object-store/rustfs/crates/s3select-api/src/test/query_execution_test.rs

## Purpose
This file tests the API crate's query output and state-machine primitives independently from the full DataFusion-backed query implementation.

## Important APIs, Types, And Functions
The tests construct `Query`, `Context`, `QueryStateMachine`, and `Output` values. They verify `QueryStateMachine::begin`, phase transition methods, `cancel`, `fail`, `duration`, `QueryType` display, `Output::Nil`, and collecting stream output.

## Control Flow
Tests build a synthetic `SelectObjectContentInput`, create queries and state machines, advance phases, and assert `QueryState` strings. Stream-output tests create empty or simple record-batch streams and call `chunk_result`, `schema`, `num_rows`, and `affected_rows`.

## State And Persistence Behavior
All state is in memory. The tests verify that state transitions mutate the `RwLock` state and that output collection consumes the stream.

## Dependencies And Integration Points
The file uses Arrow record batches, futures streams, DataFusion physical stream types, and the API crate query modules. It is registered through `src/test/mod.rs`.

## Risks And Edge Cases
The tests focus on happy-path state transitions and output counts. They do not enforce invalid transition rejection, finish behavior in real execution, or cancellation of active DataFusion streams.

## Test Signals
This is itself the test signal for API primitives. It gives confidence that `Output::Nil` and stream collection behave predictably and that state names remain stable.
