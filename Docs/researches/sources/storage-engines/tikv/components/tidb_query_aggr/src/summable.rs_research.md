# sources/storage-engines/tikv/components/tidb_query_aggr/src/summable.rs

Purpose: defines arithmetic required by SUM, AVG, and VARIANCE over supported aggregate numeric types. It abstracts zero construction, addition, subtraction, multiplication, division, and conversion from `usize`.

Important APIs and control flow: `Summable` extends `Evaluable` and `EvaluableRet`. `Decimal` implementation delegates arithmetic to TiDB decimal operators and converts codec errors into query `Result`; `Real` implementation uses floating-point arithmetic over `Real`.

State and persistence behavior: stateless helper trait. Aggregate states own the concrete `Decimal` or `Real` values and call these methods during updates/finalization.

Dependencies and integration: used by `impl_sum.rs`, `impl_variance.rs`, and AVG implementation outside this subset. It depends on `EvalContext` only for `add_assign`, though the current implementations do not use context.

Risks and test signals: decimal division calls `.unwrap()` before conversion, which can panic if decimal division returns no value. The TODO in decimal add asks whether truncation should be a warning. Coverage is indirect through aggregate tests rather than unit tests in this file.
