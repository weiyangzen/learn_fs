# sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_sum.rs

Purpose: implements `SUM` for numeric-like pushed-down aggregate inputs. It normalizes input expressions through TiDB-compatible cast insertion, then aggregates decimal or real values, with special enum/set paths that sum their numeric value/index.

Important APIs and control flow: `AggrFnDefinitionParserSum` validates a single child, takes the root field type, calls `util::rewrite_exp_for_sum_avg`, verifies the rewritten expression type equals the requested output type, appends one output column/expression, and returns `AggrFnSum<Decimal>`, `AggrFnSum<Real>`, `AggrFnSumForEnum`, or `AggrFnSumForSet`. `AggrFnStateSum<T>` stores `sum` and `has_value`, ignoring nulls and returning null until a non-null input is seen.

State and persistence behavior: state is in-memory per group. Decimal addition flows through `Summable::add_assign`, allowing decimal errors to surface through `Result`; real addition is direct. Enum and set states use `Decimal` and convert `value.value()` before adding.

Dependencies and integration: relies on `Summable`, `EvalContext`, `RpnExpression`, `VectorValueExt`, `tipb::ExprType::Sum`, and generated `AggrFunction` impls. It shares type rewrite behavior with AVG and VARIANCE through `util.rs`.

Risks and test signals: `parse_rpn` treats unexpected post-rewrite types as `unreachable!`, so rewrite and eval-type mapping must remain aligned. The comment questions decimal truncation handling. Tests cover enum/set sums, byte-to-real integration through inserted casts, null skipping, and parser rejection of mismatched output type.
