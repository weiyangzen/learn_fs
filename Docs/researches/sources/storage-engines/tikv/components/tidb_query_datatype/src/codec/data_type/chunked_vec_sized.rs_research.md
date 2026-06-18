# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_sized.rs

## Purpose
Stores nullable fixed-size/primitive evaluation values compactly using a data vector plus validity bitmap.

## Important APIs, Types, And Functions
`ChunkedVecSized<T>` stores `data: Vec<T>`, `bitmap: BitVec`, and `PhantomData<T>`. It implements private `get`, `ChunkedVec<T>`, `ChunkRef<&T>`, `From<Vec<Option<T>>>`, and `UnsafeRefInto`.

## Control Flow
Non-null rows push the value and set bitmap true. Null rows set bitmap false and push `std::mem::zeroed()` as placeholder storage. `get` returns `Some(&data[idx])` only when the bitmap is true. `truncate` trims data and bitmap. `append` drains both data and bitmap from the source vector.

## State And Persistence
In-memory only. Null rows still occupy a `T` slot to preserve O(1) indexed access.

## Dependencies And Integration Points
Used for primitive/evaluable types such as `Int`, `Real`, `Decimal`, `DateTime`, and `Duration`, and as a child vector for enums. Requires `T: Clone` for owned chunk operations and `T: Evaluable + EvaluableRet` for borrowed chunk access.

## Risks
`std::mem::zeroed()` is unsafe for arbitrary `T`; the trait implementation allows any `T: Clone`, so correctness relies on only using types where zeroed is valid. Bounds violations panic. Unsafe lifetime extension is used for evaluator plumbing.

## Test Signals
Local tests cover construction for decimal, real, duration, datetime, and int values; basics; truncation; append; plus append/iterate benches.
