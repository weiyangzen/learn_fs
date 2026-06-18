# sources/storage-engines/tikv/components/tidb_query_common/src/execute_stats.rs

Purpose: provides lightweight execution statistics for pushed-down executors and `EXPLAIN ANALYZE` support.

Important APIs and control flow: `ExecSummary` tracks processed time, produced rows, and iteration count, deriving add/add-assign for accumulation. `ExecSummaryCollector` abstracts enabled/disabled collection. `ExecSummaryCollectorEnabled` records coarse start time on iteration start, accumulates elapsed nanoseconds and produced row counts on finish, and moves counts into a target slot on collect. `ExecSummaryCollectorDisabled` compiles the same call pattern into no-ops. `ExecuteStats` bundles per-executor summaries with scanned rows per range.

State and persistence behavior: collectors keep in-memory counters until `collect`, where enabled collection drains by `mem::take`. `ExecuteStats::clear` resets summaries and scanned rows.

Dependencies and integration: depends on `tikv_util::time` and `derive_more`. Executors use these collectors around `next_batch` calls and merge storage scanned-row output.

Risks and test signals: target indexing is unchecked beyond slice indexing, so executor output index bookkeeping must be correct. `usize` counters can theoretically saturate/wrap only through extremely large workloads. Coverage is likely through executor tests rather than this file.
