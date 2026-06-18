# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_common.rs

## Purpose
Provides a macro with common `ChunkedVec` boilerplate for concrete column vector implementations.

## Important APIs, Types, And Functions
`impl_chunked_vec_common!($ty)` expands `from_slice`, `from_vec`, `push`, and `is_empty` methods for a `ChunkedVec<$ty>` implementation.

## Control Flow
`from_slice` allocates with slice length capacity and clones each optional element through `push`. `from_vec` consumes the vector and pushes each element. `push` dispatches `Some` to `push_data` and `None` to `push_null`. `is_empty` delegates to `len`.

## State And Persistence
No state of its own. It standardizes mutation behavior across chunked vectors.

## Dependencies And Integration Points
Invoked by bytes, JSON, enum, set, sized, and vector-float chunk implementations. Assumes each target type has `with_capacity`, `push_data`, `push_null`, and `len` methods from its `ChunkedVec` implementation.

## Risks
The macro clones slice elements, which can be expensive for large variable-length values. It also hides repeated behavior, so bugs in semantics are replicated across all chunked vector types.

## Test Signals
No local tests; all consumer modules exercise generated methods through their own `from_slice`, `from_vec`, and `push` tests.
