# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/vector.rs

## Purpose
Defines `VectorValue`, the dynamic column container used by vectorized query execution. It wraps per-type chunked vector storage and provides uniform APIs for capacity management, append/truncate, scalar element access, MySQL truth evaluation, binary datum encoding, and type-specific push/extract helpers.

## Important APIs, Types, And Functions
- `VectorValue`: variants for every eval type, backed by matching `ChunkedVec*` storage.
- Constructors and metadata: `with_capacity`, `from_scalar`, `clone_empty`, `eval_type`, `len`, `is_empty`, `capacity`.
- Mutation: `truncate`, `clear`, `append`, explicit `push_*` methods, and generic `VectorValueExt<T>::push`.
- Access: `get_scalar_ref` and `to_*_vec` extraction methods.
- Encoding sizing: `maximum_encoded_size` and `maximum_encoded_size_chunk`.
- Encoding: `encode` and `encode_sort_key`.

## Control Flow
Construction dispatches on `EvalType` or `ScalarValue` variants. `from_scalar` fills a typed chunked vector with repeated nulls or cloned scalar values. `append` macro-dispatches on the left-hand variant and panics if the right-hand vector has a different eval type. Boolean evaluation iterates all rows and calls `AsMySqlBool` for each nullable element. Encoding retrieves the row element, writes a null datum for missing values, or delegates to `EvaluableDatumEncoder`; bytes sort-key encoding runs through the configured collator first.

## State And Persistence Behavior
The container owns in-memory column state through chunked vectors. Null state is maintained by the chunk implementations through their `ChunkedVec` contract. Persistence only occurs when encoded datum bytes are appended to caller buffers.

## Dependencies And Integration Points
This module sits between vectorized executors and low-level chunked storage modules. It uses `ScalarValueRef` for dynamic row access, `FieldTypeAccessor` and `EvalContext` for encoding, `DECIMAL_STRUCT_SIZE` and concrete MySQL type encoders for size estimates, and collation dispatch for sort keys.

## Risks And Edge Cases
- `Set` maximum-size and encoding paths are `unimplemented!`; generic code must avoid set vectors until support exists.
- Type mismatches in `append`, `push_*`, and `to_*_vec` panic rather than returning errors.
- `maximum_encoded_size` for decimal iterates selected rows and uses approximate sizes, with a FIXME noting a maximum-size-only approach would avoid iteration.
- Chunk-format sizing for variable-width values depends on offset overhead assumptions and selected logical rows.
- `eval_as_mysql_bools` asserts output capacity and then writes by index, so callers must provide a large enough buffer.

## Test Signals
Local tests cover basic capacity/length behavior, cloning, null/value pushes, truncation, enum/set empty vector construction, append semantics, and conversion from `ChunkedVecSized`. Encoding and size-estimate behavior are tested indirectly by codec and executor tests.
