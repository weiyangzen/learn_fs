# sources/object-store/rustfs/crates/s3select-query/src/sql/logical/planner.rs

## Purpose
This file provides the default logical planner type alias/wrapper for SQL statements.

## Important APIs, Types, And Functions
`DefaultLogicalPlanner<'a, S>` wraps or aliases the generic `SqlPlanner<'a, S>` from `sql/planner.rs` for a `ContextProviderExtension`.

## Control Flow
The dispatcher constructs this planner with a `MetadataProvider`, then calls `create_logical_plan`.

## State And Persistence Behavior
Planner state is borrowed metadata context only; no persistence.

## Dependencies And Integration Points
It depends on the generic SQL planner and metadata provider extension trait.

## Risks And Edge Cases
This thin layer inherits all SQL planner limitations. Type aliases/wrappers must remain synchronized with `SqlPlanner` generics.

## Test Signals
Covered by parser/planner integration tests.
