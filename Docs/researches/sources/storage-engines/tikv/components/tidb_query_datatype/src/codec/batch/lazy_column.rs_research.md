# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/lazy_column.rs

## Purpose
Defines `LazyBatchColumn`, a column container that can remain in raw datum bytes or be decoded into a typed `VectorValue` on demand. It reduces repeated serialization/deserialization in coprocessor batch execution.

## APIs, Flow, And State
The enum variants are `Raw(BufferVec)` and `Decoded(VectorValue)`. Constructors allocate raw or decoded storage, and accessors enforce the current state with panics on wrong-state use. `ensure_decoded` converts raw entries to typed values using `EvalType::try_from(field_type.tp())`, `RawDatumDecoder`, `EvalContext`, and `LogicalRows`. For referenced logical rows it builds a decode bitmap and fills unneeded physical positions with `None`; already-decoded columns are left unchanged. Encoding APIs either copy raw datum bytes, delegate to `VectorValue::encode`, or build chunk `Column` values for chunk output.

## Dependencies And Integration
Depends on `BufferVec`, `FieldType`, `EvalType`, `VectorValue`, `ChunkColumnEncoder`, `Column`, datum decoding, and `EvalContext`. It is used by `LazyBatchColumnVec` and batch executors as the bridge between storage datum format and TiDB chunk format.

## Risks And Test Signals
Risks include panics from wrong-state accessors, type/field mismatches during decode, and subtle physical versus logical row layout assumptions. Tests cover raw/decoded transitions, selective decode behavior, clone semantics, encoding, and benches compare `BufferVec` against vector-backed raw storage.
