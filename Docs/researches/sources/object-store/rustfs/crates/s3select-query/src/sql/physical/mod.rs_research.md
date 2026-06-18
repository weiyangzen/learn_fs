# sources/object-store/rustfs/crates/s3select-query/src/sql/physical/mod.rs

## Purpose
This module exposes physical SQL planning and optimization components.

## Important APIs, Types, And Functions
It declares `pub mod optimizer;` and `pub mod planner;`.

## Control Flow
No local logic.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`CascadeOptimizer` imports the default physical planner through this module.

## Risks And Edge Cases
Future physical stages must be exported here.

## Test Signals
No direct tests.
