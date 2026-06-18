# sources/object-store/rustfs/crates/s3select-query/src/execution/mod.rs

## Purpose
This module declares query execution submodules.

## Important APIs, Types, And Functions
It exports `factory`, `query`, and `scheduler`.

## Control Flow
No local logic exists. It is the namespace for concrete execution components.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`instance` and dispatcher code import execution factory and local scheduler through this module.

## Risks And Edge Cases
New scheduler or execution variants must be exported here.

## Test Signals
No direct tests; execution is covered by integration tests.
