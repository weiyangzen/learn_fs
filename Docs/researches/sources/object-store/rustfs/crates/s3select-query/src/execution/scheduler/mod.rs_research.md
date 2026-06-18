# sources/object-store/rustfs/crates/s3select-query/src/execution/scheduler/mod.rs

## Purpose
This module exposes execution scheduler implementations.

## Important APIs, Types, And Functions
It declares `pub mod local;`.

## Control Flow
No local logic.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
`LocalScheduler` is imported by `instance` and `lib` global component setup.

## Risks And Edge Cases
Future schedulers require exports here.

## Test Signals
No local tests.
