# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/scalar.rs

## Purpose
Defines dynamic single-value containers for all eval types. `ScalarValue` owns an optional value, while `ScalarValueRef` borrows an optional value from a scalar or vector. The file also implements binary datum encoding, sort-key encoding/comparison, typed accessors, and conversions between owned and borrowed representations.

## Important APIs, Types, And Functions
- `ScalarValue`: variants for `Int`, `Real`, `Decimal`, `Bytes`, `DateTime`, `Duration`, `Json`, `Enum`, `Set`, and `VectorFloat32`, each wrapping `Option`.
- `ScalarValueRef<'a>`: borrowed counterpart using references or specialized ref types such as `JsonRef`, `EnumRef`, `SetRef`, and `VectorFloat32Ref`.
- `eval_type`, `as_scalar_value_ref`, `is_none`, `is_some`, and `to_owned`.
- `encode` and `encode_sort_key`: write evaluable datum bytes according to `FieldType` and `EvalContext`.
- `cmp_sort_key`: compares two scalar refs with unsigned integer handling and collation-aware byte comparison.
- `compare_int`: switches signed vs unsigned ordering using `FieldType::is_unsigned`.
- `impl_from!` and `impl_as_ref!`: provide typed conversions and accessors.

## Control Flow
Owned values convert to borrowed refs by mapping `Option<T>` to `Option<&T>` or specialized refs. Encoding matches the variant, writes null flags for `None`, and otherwise delegates to `EvaluableDatumEncoder`. Integer encoding checks field unsignedness and emits either signed or unsigned datum form. Byte sort-key encoding first computes a collation sort key and then encodes that byte sequence. Sort-key comparison uses normal option ordering for most variants, a custom unsigned-aware path for integers, and collator-specific byte comparison for bytes.

## State And Persistence Behavior
`ScalarValue` owns in-memory values; `ScalarValueRef` borrows them. Persistence happens only through datum encoding into caller-provided byte buffers. There is no file or database state in this module.

## Dependencies And Integration Points
Integrates with `tipb::FieldType`, `EvalContext`, `EvaluableDatumEncoder`, collator dispatch, `EvalType`, and MySQL concrete types. It is used by expression evaluation, vector element access, result encoding, and sorting code that needs dynamic scalar handling.

## Risks And Edge Cases
- `Enum` and `Set` scalar encoding are explicitly `unimplemented!`, so routing those values through generic encode paths can panic.
- `From<Option<f64>>` and `From<f64>` map NaN to `None` because `Real::new` rejects NaN; callers must not confuse this with SQL NULL semantics unless intended.
- Wrong-type conversions from `ScalarValue` into `Option<T>` panic with the dynamic eval type in the message.
- `cmp_sort_key` panics for cross-type comparisons and depends on correct `FieldType` collation/unsigned metadata.
- Accessor panic messages for enum/set mention `Int`, which may make diagnosis less precise.

## Test Signals
This file has no local test module. It is exercised indirectly by `VectorValue::get_scalar_ref`, codec encode tests, collated sorting, and expression evaluation tests. Missing direct tests include scalar encode for all supported types, unsigned integer comparison, collation sort-key behavior, and confirmation that enum/set encode panics are not hit by supported paths.
