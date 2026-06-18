# sources/object-store/rustfs/crates/s3select-api/src/query/function.rs

## Purpose
This file defines the function metadata manager abstraction used by the SQL planner to resolve scalar, aggregate, and window UDFs.

## Important APIs, Types, And Functions
`FuncMetaManagerRef` is an `Arc<dyn FunctionMetadataManager + Send + Sync>`. `FunctionMetadataManager` supports registering and looking up `ScalarUDF`, `AggregateUDF`, and `WindowUDF`, and listing names for each category.

## Control Flow
Concrete managers receive registrations during setup and are later queried by the metadata provider while DataFusion resolves functions.

## State And Persistence Behavior
The trait has mutating registration methods, but persistence is left to implementations. The default implementation keeps in-memory hash maps.

## Dependencies And Integration Points
It depends on DataFusion UDF types and `QueryResult`. `SimpleFunctionMetadataManager` implements this trait and is injected into `MetadataProvider`.

## Risks And Edge Cases
Lookup semantics, duplicate registration behavior, and case sensitivity are not specified in the trait; implementations must define and test these choices.

## Test Signals
No local tests. Function-manager behavior is covered by its implementation and by query planning failures for unresolved functions.
