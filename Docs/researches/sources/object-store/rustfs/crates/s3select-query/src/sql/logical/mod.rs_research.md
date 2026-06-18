# sources/object-store/rustfs/crates/s3select-query/src/sql/logical/mod.rs

## Purpose
This module exposes logical SQL planner and optimizer components.

## Important APIs, Types, And Functions
It declares `pub mod optimizer;` and `pub mod planner;`.

## Control Flow
No local logic.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`CascadeOptimizer` and dispatcher planning import logical components from here.

## Risks And Edge Cases
Future logical stages must be exported here.

## Test Signals
No local tests.
