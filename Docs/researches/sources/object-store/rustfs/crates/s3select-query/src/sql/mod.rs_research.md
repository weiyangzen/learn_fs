# sources/object-store/rustfs/crates/s3select-query/src/sql/mod.rs

## Purpose
This module exports the SQL stack for the query crate.

## Important APIs, Types, And Functions
It declares `analyzer`, `dialect`, `logical`, `optimizer`, `parser`, `physical`, and `planner`.

## Control Flow
No local logic.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
The dispatcher, instance construction, and optimizer import SQL components through this namespace.

## Risks And Edge Cases
Adding SQL pipeline stages requires updating this module.

## Test Signals
No direct tests.
