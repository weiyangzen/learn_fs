# Research: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_avg.rs

## sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_avg.rs

Purpose: implements vectorized AVG aggregate parsing and state for Decimal, Real, Enum, and Set inputs. AVG returns two partial result columns, `(count, sum)`, which TiDB can finalize into an average.

Important APIs are `AggrFnDefinitionParserAvg`, generic `AggrFnAvg<T>`, `AggrFnStateAvg<T>`, and special enum/set aggregate/state pairs. The parser verifies `ExprType::Avg`, requires one child, rewrites the child expression for SUM/AVG typing, checks the rewritten return type matches the encoded sum field type, appends unsigned `LongLong` count plus sum field type to output schema, and returns the correct aggregate implementation.

Control flow in state updates ignores NULLs, adds non-null values to `sum` through `Summable::add_assign`, and increments `count`. Enum and Set convert their numeric value to `Decimal`. `push_result` writes count and either NULL sum for empty input or the accumulated sum. State is only `sum` and `count`; no persistence.

Dependencies include aggregate codegen macros, datatype vector abstractions, EvalContext, RPN expressions, `tipb`, and utility expression rewriting. Risks include type mismatch between TiDB field metadata and rewritten expression, decimal overflow/error propagation through `EvalContext`, and count stored as `usize` then cast to TiDB `Int`. Test signals cover scalar/vector updates, NULL handling, enum/set conversion, integration parsing/evaluation, and illegal request rejection.
