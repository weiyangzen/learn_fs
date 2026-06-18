# sources/storage-engines/tikv/components/tidb_query_executors/src/util/aggr_executor.rs

## Purpose

`util/aggr_executor.rs` provides the shared aggregation executor framework used by simple, hash, and stream aggregation implementations. It parses aggregate definitions, owns common aggregation entities, drives source consumption, coordinates paging/drain semantics, materializes aggregate results, and forwards batch executor plumbing.

## Important APIs, Types, and Functions

- `AggregationExecutorImpl<Src>` is the strategy trait implemented by concrete aggregation modes. It defines `prepare_entities`, `process_batch_input`, `groups_len`, `iterate_available_groups`, and `is_partial_results_ready`.
- `Entities<Src>` bundles shared mutable state: source executor, `EvalContext`, output schema, aggregate function objects, per-function result cardinalities, aggregate argument RPN expressions, and result eval types.
- `AggregationExecutor<Src, I>` owns an implementation, `Entities`, an ended flag, and optional paging row target.
- `AggregationExecutor::new` parses protobuf aggregate expressions through an `AggrDefinitionParser`, builds result schema and aggregate argument expressions, computes result eval types, creates `Entities`, and lets the implementation append group-by fields.
- `handle_next_batch` consumes source batches at `BATCH_MAX_SIZE`, propagates warnings, delegates input processing, applies paging drain rules, and decides whether partial results are available.
- `aggregate_partial_results` allocates result columns by aggregate output eval type, asks the implementation to iterate available groups, pushes aggregate state results, appends group-by columns, and verifies column lengths.

## Control Flow

`next_batch` ignores the caller's `scan_rows` and asks `handle_next_batch` for any available aggregate output. The source is always polled at max batch size because aggregation must process all relevant rows or all currently available partial groups. If the source returns an error, the executor stops and returns empty output with the error. If the source has rows, the concrete implementation updates its group/global states. Paging compares `groups_len` with `required_row`; when enough groups exist it changes the drain state to `PagingDrain`. For partial-capable implementations such as stream aggregation, `required_row` is adjusted to account for groups that can be returned before full source drain.

When results are available, `aggregate_partial_results` invokes the implementation's `iterate_available_groups`. The callback receives the aggregate states for one group at a time and calls `push_result` on each state, respecting multi-column aggregate outputs such as AVG's count/sum cardinality. The return columns are aggregate result columns followed by any group-by columns supplied by the implementation.

## State and Persistence Behavior

State is in-memory and generic over the source executor. `Entities.context` holds warnings and evaluation settings, including paging size. `required_row` persists paging progress across calls. Concrete implementations own aggregate states and group metadata. `is_ended` prevents calls after drain/error. There is no durable persistence.

## Dependencies and Integration Points

The module depends on `tidb_query_aggr` for aggregate function parsing/state, `tidb_query_expr::RpnExpression`, `tidb_query_datatype` vector/value types and eval context/config, `tipb::Expr`/`FieldType`, and the crate `BatchExecutor` interface. It is the integration layer used by slow hash, fast hash, stream, and likely simple aggregation executors. It forwards intermediate-result, execution stats, storage stats, scanned range, and cacheability calls to the source executor.

## Risks and Edge Cases

- The parser asserts each aggregate currently has exactly one argument expression; adding multi-argument aggregate functions would require changes.
- Errors from the source suppress aggregate output even if prior state exists.
- Paging behavior depends on concrete `groups_len` semantics. For stream aggregation, `groups_len` includes the partial trailing group, so wrapper logic adjusts `required_row`.
- `all_result_column_types` uses `EvalType::try_from(...).unwrap()` because aggregate parsers are expected to produce supported types; parser bugs can panic.
- `scan_rows` passed to aggregation `next_batch` is intentionally ignored, which can surprise consumers expecting strict row budgeting.

## Test Signals

The test module defines unreachable aggregate machinery, reusable mock sources, and `test_agg_paging`. Paging tests compare fast hash, slow hash, and stream aggregation behavior with paging sizes 2, 5, and 7, validating call counts, drain states, and output row counts. The shared fixtures include nulls, empty logical batches, multiple physical rows, and multi-batch sources.
