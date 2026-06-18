# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/mod.rs

## Purpose
This is the central dynamic data-type facade for TiKV query evaluation. It declares concrete eval-type aliases, re-exports chunked vector storage implementations, and defines traits that connect concrete Rust values, borrowed references, scalar containers, and vector containers to TiDB `EvalType` metadata.

## Important APIs, Types, And Functions
- Module exports: chunked vectors for bytes, JSON, enum, set, sized scalar values, vector float32, bit vectors, `ScalarValue`, `ScalarValueRef`, `VectorValue`, and `VectorValueExt`.
- Type aliases: `Int = i64`, `Real = NotNan<f64>`, `Bytes = Vec<u8>`, and `BytesRef<'a> = &'a [u8]`.
- `match_template_evaltype!`: expands code over `Int`, `Real`, `Decimal`, `Bytes`, `DateTime`, `Duration`, `Json`, `Set`, `Enum`, and `VectorFloat32`.
- `AsMySqlBool`: converts concrete eval values and nullable references into MySQL truth values.
- `ChunkRef`, `ChunkedVec`, `Evaluable`, `EvaluableRet`, and `EvaluableRef`: generic contracts for vector storage, scalar borrowing, return-vector construction, and reference-to-owned conversion.
- `UnsafeRefInto`: intentionally unsafe lifetime widening helper used by aggregation macros.

## Control Flow
Most behavior is macro-expanded over eval types. `AsMySqlBool` implementations encode MySQL truth rules: numeric zero is false, bytes parse through `ConvertTo<f64>`, JSON delegates to `JsonRef::is_zero`, vector-float values are true when non-empty, and nullable wrappers are false on `None`. `Evaluable` and `EvaluableRef` perform dynamic enum variant checks and panic on mismatches, with special conversions for `Enum` as `Int` or `Bytes`. `EvaluableRet` converts concrete chunked storage back to `VectorValue`.

## State And Persistence Behavior
This module owns no persistent state. It defines in-memory contracts for columnar execution. The key state invariant is in `ChunkedVec`: the null bitmap and value buffer must be mutated together so equality and stored representations remain coherent for null rows.

## Dependencies And Integration Points
It bridges `EvalType`, `FieldTypeAccessor`, MySQL codec types, collations, conversion traits, `EvalContext`, and vector/scalar containers. Aggregation code relies on `UnsafeRefInto`; vectorized expression code relies on `Evaluable` and `EvaluableRef`; codec paths rely on exported concrete types and `AsMySqlBool`.

## Risks And Edge Cases
- Many wrong-type paths intentionally panic rather than return `Result`, so framework-level dispatch must keep `EvalType` and container variants aligned.
- Unsafe lifetime transmute is explicitly documented as used by aggregation update macros; misuse outside that pattern could create dangling references.
- Enum coercions reinterpret enum numeric values as `i64` via pointer casting; this is performance-sensitive and depends on representation assumptions.
- `BytesRef` truth conversion can return conversion errors for malformed numeric strings.
- `Set` support exists at the type-trait layer but encoding/decoding support is incomplete elsewhere.

## Test Signals
Local tests cover byte-to-bool conversion, parse errors, infinities, and `Real` truth conversion including NaN rejection via `NotNan`. Broader trait coverage is indirect through scalar/vector tests and expression evaluation tests.
