# Research: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_count.rs

## sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_count.rs

Purpose: implements vectorized COUNT aggregate parsing and state. COUNT outputs one unsigned `LongLong` partial result representing the number of non-null evaluated child values.

Important APIs are `AggrFnDefinitionParserCount`, `AggrFnCount`, and `AggrFnStateCount`. The parser verifies `ExprType::Count`, requires one child, appends an unsigned `LongLong` output field, stores the child RPN expression, and returns `AggrFnCount`.

Control flow is optimized manually rather than using only concrete state macros. `update` increments for a non-null scalar value. `update_repeat` adds `repeat_times` for repeated non-null constants such as `COUNT(1)`. `update_vector` iterates logical row indexes and counts non-null physical values. `push_result` writes the count as `Int`. State is a `usize` counter; no persistence.

Dependencies include aggregate codegen, datatype vector traits, EvalContext, RPN expressions, and `tipb` field metadata. Risks include `usize` to `Int` casting on extremely large groups, correctness depending on logical row indexes matching evaluated chunks, and parser acceptance of only one-child COUNT forms. Test signals cover null vs non-null scalar updates, repeated updates, vector updates over selected rows, and enum/set references.
