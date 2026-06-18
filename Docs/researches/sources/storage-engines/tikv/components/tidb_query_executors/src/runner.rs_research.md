# sources/storage-engines/tikv/components/tidb_query_executors/src/runner.rs

## Purpose

`runner.rs` is the batch coprocessor DAG runner. It validates supported tipb executor descriptors, builds a tree of vectorized `BatchExecutor`s from a `DagRequest`, drives that tree until drain, paging, streaming row limits, deadlines, or `max_keys_read` limits are reached, and encodes main and intermediate results into `SelectResponse` or `StreamResponse`.

## Important APIs, Types, and Functions

- `BATCH_INITIAL_SIZE`, exported `BATCH_MAX_SIZE`, and `BATCH_GROW_FACTOR` control adaptive batch size growth. Failpoints can override initial and growth factor values in tests.
- `IntermediateOutputChannel` records encode type, output offsets, and schema for intermediate outputs, primarily index lookup.
- `BatchExecutorsRunner<SS>` owns the root executor, request output offsets, eval config, execution stats, stream/paging/max-key controls, quota limiter, intermediate channel state, and reusable intermediate result buffers.
- `BatchExecutorsRunner<()>::check_supported(exec_descriptors)` validates each descriptor and rejects unsupported executor types such as joins, windows, sorts, exchanges, CTEs, and partition table scan.
- `is_arrow_encodable(schema_iter)` checks whether requested output field types support chunk encoding; unsupported fields force default row encoding.
- `is_executor_under_parent_tp(under_tp, executor, executor_index, left_executors)` walks explicit or natural parent links to detect whether an executor is under a parent type such as `TypeIndexLookUp`.
- `build_executors(...)` builds the executor chain/tree from tipb descriptors, storage, ranges, config, intermediate output descriptors, and optional region storage accessor.
- `from_request(...)` builds `EvalConfig`, injects paging and `max_keys_read`, builds executors, validates output offsets, chooses response encode types, and initializes runner state.
- `handle_request()` runs a non-streaming request and returns `(SelectResponse, Option<IntervalRange>)`.
- `handle_streaming_request()` returns one streaming `StreamResponse` chunk plus scanned range until the stream drains.
- `internal_handle_request(...)` performs one root `next_batch`, encodes main rows, merges warnings, and drains intermediate outputs.
- `consume_and_encode_intermediate_results(...)` pulls intermediate batches from executors and encodes them into their channel chunk vectors.
- `make_stream_response(...)` serializes a stream chunk, attaches scan stats and warnings, records iteration metrics, and clears execution stats for the next stream response.
- `encode_result_to_chunk(...)` serializes a `BatchExecuteResult` with default datum encoding for streaming/default mode or chunk encoding otherwise.
- `grow_batch_size(...)` doubles the batch size up to `BATCH_MAX_SIZE`.

## Executor Construction Flow

`build_executors` requires the first descriptor to be a table scan or index scan. It creates the bottom executor with scan summary collection and increments executor count metrics. For index scans under index lookup with common handles, it detects the parent relation so the scan can fill extra common handle keys.

The builder then walks the remaining descriptors using `parent_idx` to support a mostly linear chain plus index lookup's table-scan child. It wraps the current executor for selection, projection, simple aggregation, fast or slow hash aggregation, stream aggregation, limit, top n, partition top n, and index lookup. Limit descriptors with `partition_by` are treated as partition TopN without order keys. TopN descriptors with `partition_by` are routed to `BatchPartitionTopNExecutor`; otherwise to `BatchTopNExecutor`.

For `TypeIndexLookUp`, exactly one buffered child descriptor must exist and it must be `TypeTableScan`. The builder finds exactly one matching intermediate output channel, then calls `build_index_lookup_executor` with either `CommonHandle` or `IntHandle` depending on table scan primary column metadata. After each wrapper, unhandled children or invalid parent indexes cause immediate errors.

## Request Execution Flow

`from_request` consumes a `DagRequest` and prepares execution. It copies request execution-summary settings, creates `EvalConfig::from_request`, stores paging and `max_keys_read` in the config, and marks scans as range-aware when streaming, paging, or max-key stopping may require resume ranges. It validates main output offsets and chooses `EncodeType::TypeDefault` if any requested output field cannot be chunk-encoded. It repeats the same offset and encoding checks for intermediate channels using `out_most_executor.intermediate_schema(idx)`.

`handle_request` starts at `BATCH_INITIAL_SIZE` and loops. Each iteration:

1. Checks quota/cpu sampling around `internal_handle_request`.
2. Adds read bytes and applies quota limiter delay metrics.
3. Adds produced main/intermediate record counts.
4. When `max_keys_read` is enabled, peeks cumulative scanned rows via `out_most_executor.peek_scanned_rows_sum()` without draining stats.
5. Pushes non-empty chunks.
6. Stops on executor drain, paging output count, or scanned-key budget.

On stop it collects execution stats once, records total executor iterations, optionally returns scanned range when not fully drained and paging or `max_keys_read` caused partial execution, builds `SelectResponse`, attaches intermediate outputs, output counts, optional execution summaries, warnings, and encode type, then returns. If not stopped, it grows batch size.

`handle_streaming_request` does not allow intermediate channels. It repeatedly calls `internal_handle_request` until `stream_row_limit` is reached or the executor drains, concatenates rows data into one chunk, and returns `None` only when drained with no rows.

## State and Persistence Behavior

The runner has no durable persistence. Per-request mutable state includes:

- `exec_stats`: accumulated per-executor iteration, produced row, processed time, and scanned rows. Non-streaming clears only when runner is dropped; streaming clears after each response.
- `reserved_intermediate_results`: lazily allocated vectors reused to avoid repeated intermediate result allocation.
- `config`: shared immutable `Arc<EvalConfig>` with request flags plus paging and max-key controls.
- `deadline`: checked at each internal batch.
- `quota_limiter`: shared limiter used to sample CPU/read bytes and delay if needed.

Scanned ranges are delegated to the executor tree. The runner returns an `IntervalRange` only for partial paging/max-key/streaming paths, not for full drain. `max_keys_read` is explicitly best-effort inside TiKV; authoritative global enforcement is documented as living in TiDB.

## Dependencies and Integration Points

`runner.rs` is the integration hub for this directory. It directly references table scan, index scan, selection, projection, simple/hash/stream aggregation, limit, top n, partition top n, and index lookup executors. External dependencies include:

- `tipb` request/response/executor protobuf types.
- `kvproto::coprocessor::KeyRange` and storage abstractions from `tidb_query_common::storage`.
- `api_version::KvFormat` for storage key/value format specialization.
- `tidb_query_datatype` for field type, eval config/context, table handles, and encoding support.
- `tikv_util::deadline::Deadline` and `QuotaLimiter` for request limits and resource throttling.
- `protobuf::Message` for stream response serialization.
- Metrics in `tidb_query_common::metrics` and `tikv_util::metrics`.

The runner's output chunks are consumed by the coprocessor response layer. Its `collect_storage_stats`, `collect_scan_summary`, and `can_be_cached` methods are integration hooks for surrounding request handling.

## Risks and Edge Cases

- Parent index handling is delicate. Explicit `parent_idx` must be greater than the current index and within the descriptor list. Incorrect descriptors fail during build.
- Chunk encoding fallback is per requested output schema. Adding new field types without `EvalType` support silently falls back to default encoding, which affects response format and performance.
- Intermediate output channels must match executor indexes and schemas. Index lookup currently requires exactly one intermediate channel.
- `max_keys_read` uses `peek_scanned_rows_sum` from scan stats and intentionally avoids draining stats before final collection. Any executor that buffers scans without reflecting scan counts can under-report; the code notes index lookup pushdown is disabled elsewhere when max-key limiting is set.
- `handle_request` counts intermediate rows toward `record_all` for paging, not only main output rows. This is intentional in current code but important for response-size behavior.
- Streaming mode concatenates row data and always uses default-like serialization through `encode_result_to_chunk` because `is_streaming` forces row encoding.
- Deadline errors abort the request before encoding later batches. Quota limiter delay is applied after each internal batch, so large single batches can still do work before throttling.

## Test Signals

Tests cover chunk/default encoding correctness, index lookup executor construction and error cases, runner construction with intermediate channels and encoding fallback, intermediate output encoding and buffer reuse, response intermediate output attachment, non-streaming handle_request including paging and intermediate rows, parent traversal helper validation, and `max_keys_read` early stopping, unlimited mode, high limits, exact limits, and natural drain before limit. Failpoint-aware batch size helpers are also testable.
