# sources/object-store/rustfs/crates/s3select-query/src/function/simple_func_manager.rs

## Purpose
This file implements an in-memory function metadata manager for DataFusion scalar, aggregate, and window UDFs.

## Important APIs, Types, And Functions
`SimpleFunctionMetadataManager` stores three `HashMap<String, Arc<...>>` collections for scalar, aggregate, and window UDFs. `Default` seeds the maps from DataFusion `SessionStateDefaults`. The trait implementation registers functions by name, resolves names, and returns name lists.

## Control Flow
Construction loads DataFusion built-ins/defaults, logging counts. Registration inserts by function name. Lookup returns a cloned `Arc` or a `QueryError::Datafusion`/lookup-style error when missing, depending on helper path.

## State And Persistence Behavior
All function metadata is in memory. The global DB path reuses a single `Arc<SimpleFunctionMetadataManager>`; fresh DB creation builds a new manager.

## Dependencies And Integration Points
It depends on DataFusion UDF types and default function registries, API `FunctionMetadataManager`, and `QueryError`. `MetadataProvider` calls it for UDF lookup.

## Risks And Edge Cases
The manager is not internally synchronized for mutation after sharing as an `Arc`; registrations require `&mut self`, so runtime mutation is effectively setup-only. Duplicate names overwrite prior entries. Name matching is exact and may be case-sensitive relative to SQL normalization.

## Test Signals
No local tests. Function resolution is indirectly tested through successful built-in SQL queries and unresolved-function error cases.
