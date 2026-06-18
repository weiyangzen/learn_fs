# sources/object-store/rustfs/crates/s3select-query/src/function/mod.rs

## Purpose
This module exposes function metadata manager implementations.

## Important APIs, Types, And Functions
It declares `pub mod simple_func_manager;`.

## Control Flow
No local logic.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`SimpleFunctionMetadataManager` is used by `instance`, `lib`, and `MetadataProvider` to resolve UDFs.

## Risks And Edge Cases
New function managers must be exported here.

## Test Signals
No local tests.
