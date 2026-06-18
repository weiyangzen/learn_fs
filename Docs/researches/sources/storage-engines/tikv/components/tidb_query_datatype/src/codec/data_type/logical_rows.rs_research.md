# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/logical_rows.rs

## Purpose
Defines the logical row indirection used by TiKV vectorized expression evaluation. `LogicalRows` represents either the identity row mapping for a batch or a borrowed slice of selected physical row indexes. This lets callers distinguish the common "all rows in physical order" case from a filtered/reordered selection without always materializing a `Vec<usize>`.

## Important APIs, Types, And Functions
- `BATCH_MAX_SIZE`: fixed batch cap of `1024`, documented as inherited from MonetDB/X100-style batch sizing rather than TiKV-specific benchmarks.
- `IDENTICAL_LOGICAL_ROWS`: compile-time initialized `[usize; BATCH_MAX_SIZE]` containing `0..BATCH_MAX_SIZE`.
- `LogicalRows<'a>`: `Identical { size }` for identity mappings and `Ref { logical_rows }` for borrowed index slices.
- `new_ident`, `from_slice`, `as_slice`, `get_idx`, `is_ident`, `len`, and `is_empty`: the core accessors used by evaluation code.
- `LogicalRowsIterator`: drives `IntoIterator` over either mapping mode.

## Control Flow
The identity path avoids dereferencing a slice in `get_idx` by returning the requested logical position. The borrowed path indexes into the supplied slice. `as_slice` bridges older call sites that still expect `&[usize]`; it returns a slice into `IDENTICAL_LOGICAL_ROWS` for identity mappings and panics if the requested identity size is at or above the static batch limit. Iteration repeatedly calls `len` and `get_idx`, increments its internal cursor, and ends after the logical row count.

## State And Persistence Behavior
There is no persistence or mutation beyond the iterator cursor. `LogicalRows` itself is `Copy` and only carries a size or borrowed slice. The static identity array is read-only process state and has no external serialization.

## Dependencies And Integration Points
This module is re-exported by `data_type/mod.rs` and underpins vectorized evaluation routines that accept logical row selections. It integrates with `VectorValue` encoding and evaluation paths indirectly because callers use logical rows to select physical vector indexes.

## Risks And Edge Cases
- `as_slice` is a compatibility escape hatch with a panic boundary for identity mappings whose size is not less than `BATCH_MAX_SIZE`; callers should prefer `get_idx` or iteration.
- `get_idx` does not bounds-check identity size against `idx` beyond normal slice behavior in the `Ref` case; callers must respect `len`.
- The batch size constant has a TODO noting lack of local benchmarking, so performance tuning may depend on assumptions from other systems.

## Test Signals
This file has no local tests. Coverage is likely indirect through vectorized evaluator tests that exercise filtered and identity logical row paths. Useful missing tests would cover `Identical` iteration, `Ref` iteration, empty mappings, and the `as_slice` panic boundary.
