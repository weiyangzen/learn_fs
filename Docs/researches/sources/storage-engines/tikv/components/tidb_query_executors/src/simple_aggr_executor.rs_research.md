# sources/storage-engines/tikv/components/tidb_query_executors/src/simple_aggr_executor.rs

## Purpose

`simple_aggr_executor.rs` implements aggregation without `GROUP BY` for the vectorized batch executor framework. It wraps the generic `AggregationExecutor` with `SimpleAggregationImpl`, maintaining one aggregate state set for the entire input stream and producing at most one output row when the child drains and at least one input row was seen.

## Important APIs, Types, and Functions

- `BatchSimpleAggregationExecutor<Src>(AggregationExecutor<Src, SimpleAggregationImpl>)` is a thin newtype wrapper that implements `BatchExecutor` by delegating to the generic aggregation executor.
- `check_supported(descriptor: &Aggregation)` asserts no group-by expressions, rejects empty aggregate definitions, and validates every aggregate definition through `AllAggrDefinitionParser`.
- `new(config, src, aggr_defs)` and test-only `new_for_test` call `new_impl` with an aggregate definition parser.
- `new_impl(...)` constructs `SimpleAggregationImpl { states: Vec::new(), has_input_rows: false }` and passes it to `AggregationExecutor::new`.
- `SimpleAggregationImpl` stores aggregate function states and a flag indicating whether any input rows have been processed.
- `prepare_entities(entities)` creates one state per aggregate function from `entities.each_aggr_fn` and clears `has_input_rows`.
- `process_batch_input(entities, input_physical_columns, input_logical_rows)` evaluates each aggregate argument expression and updates its state with either repeated scalar values or vector values.
- `groups_len()` returns `1` only after input rows have been seen.
- `iterate_available_groups(entities, src_is_drained, iteratee)` asserts the source is stopped, calls the result-pushing iteratee for the single state group if input exists, and returns no group-by columns.
- `is_partial_results_ready()` always returns false because simple aggregation emits only after full source drain.

## Control Flow

The generic aggregation executor owns the outer batching loop. `SimpleAggregationImpl` supplies the no-grouping behavior. At prepare time it creates all aggregate states from parsed aggregate function definitions. For every non-final input batch, `process_batch_input` receives child physical columns and logical rows. It marks `has_input_rows` when the logical row slice is non-empty and records approximate work as `rows * aggregate_expression_count` under executor name `batch_simple_aggr`.

For each aggregate expression, it evaluates the argument RPN expression against the child schema and current logical rows. Scalar results are applied with `update_repeat!`, which updates the state once per logical row using the same scalar value. Vector results use the vector's logical row mapping and `update_vector!`. Typed dispatch is handled by `match_template_evaltype!`, so the aggregate state receives its expected concrete value type.

When the child drains, the generic aggregation executor asks whether partial groups are ready and then iterates available groups. Simple aggregation only emits after `src_is_drained.stop()` and only when `has_input_rows` is true. The iteratee pushes aggregate state outputs into result vectors; there are no grouping key columns to append.

## State and Persistence Behavior

State is in-memory and per request:

- `states`: boxed aggregate function states, one per aggregate definition.
- `has_input_rows`: controls whether a no-group aggregation should emit a row.

There is no durable persistence. The comment explains a deliberate semantic choice: for TiKV first-stage aggregation, a no-input simple aggregation returns no row even though SQL final-stage no-group aggregation often returns one row. This avoids producing final-stage semantics in a pushdown executor until aggregation stage metadata is introduced.

All scan/storage/range stats and cache behavior are delegated through the wrapped generic `AggregationExecutor`.

## Dependencies and Integration Points

This file integrates with:

- `tidb_query_aggr` traits and macros, including aggregate function definitions and state update macros.
- `crate::util::aggr_executor::{AggregationExecutor, AggregationExecutorImpl, Entities, AggrDefinitionParser, AllAggrDefinitionParser}`.
- `tidb_query_expr::RpnStackNode` for evaluated aggregate arguments.
- `tidb_query_datatype::codec::batch::{LazyBatchColumn, LazyBatchColumnVec}` and typed `VectorValue`s.
- `runner.rs`, which selects this executor for `TypeAggregation` and `TypeStreamAgg` descriptors when `group_by` is empty.

The output schema is produced by aggregate definition parsing, not by this file directly. The generic aggregation executor handles final result column construction and warning/error propagation around this implementation.

## Risks and Edge Cases

- The file asserts `descriptor.get_group_by().len() == 0` in `check_supported`; callers must route grouped aggregations elsewhere.
- No-input behavior intentionally returns no rows for first-stage TiKV aggregation. Changing final-stage behavior requires explicit stage information to avoid SQL semantic regressions.
- Aggregate argument evaluation errors propagate through the generic executor and stop output for the current request.
- `iterate_available_groups` asserts drained source. Calling it early would panic, but `is_partial_results_ready` returns false to prevent that path.
- State vector length must match aggregate expression count; `process_batch_input` asserts this invariant.
- Work metrics are approximate and do not account for aggregate function complexity.

## Test Signals

Tests define custom aggregate functions and parsers to validate state preparation, scalar and vector updates, multi-column aggregate outputs, constants and nulls, integration with built-in `COUNT` and `AVG`, no-input behavior, and multi-batch drain behavior. Assertions cover output row count, output column count, decoded aggregate values, and drain states.
