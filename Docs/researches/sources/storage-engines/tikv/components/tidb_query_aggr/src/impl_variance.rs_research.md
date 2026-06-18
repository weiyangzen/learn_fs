# sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_variance.rs

Purpose: implements population variance (`Variance`, `VarPop`) and sample variance (`VarSamp`) aggregates. The file uses a `VarianceType` strategy trait to choose expression matching and final denominator while sharing incremental variance accumulation.

Important APIs and control flow: `AggrFnDefinitionParserVariance<V>` validates one child, rewrites input like SUM/AVG, checks output type, and appends three output columns: unsigned count, sum, and variance. `AggrFnStateVariance<T,V>` updates count, sum, and accumulated variance using an online formula: after incrementing count and sum, it derives `t = count * input - sum` and adds `(t*t)/(count*(count-1))`. Enum/set variants convert values to `Decimal` before the same formula.

State and persistence behavior: state tracks `count`, `sum`, and accumulated variance in memory. `push_result` always emits count; sum and final variance are null when count is zero. Sample variance divides by `count - 1`, so callers must avoid requesting sample final variance for count 1 unless the surrounding SQL semantics handle it.

Dependencies and integration: shares `Summable` arithmetic, `rewrite_exp_for_sum_avg`, `FieldTypeBuilder`, aggregate update macros, and `tipb` expression kinds. Parser dispatch maps variance expression names to either `Population` or `Sample`.

Risks and test signals: `rewrite_exp_for_sum_avg(...).unwrap()` assumes casts always build; panic risk exists if cast construction changes. Decimal division and overflow/truncation errors propagate through `Result`. Tests cover enum/set variance, population and sample integration from string inputs through casts, output schema shape, and illegal output type.
