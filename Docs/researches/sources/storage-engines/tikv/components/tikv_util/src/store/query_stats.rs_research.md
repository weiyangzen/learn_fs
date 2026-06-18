# sources/storage-engines/tikv/components/tikv_util/src/store/query_stats.rs

## Purpose
Wraps `pdpb::QueryStats` with arithmetic helpers for per-query-kind counters and read-query aggregation.

## Important APIs, Types, and Functions
- `QUERY_KINDS` lists supported kinds excluding `Others`.
- `QueryStats(pub pdpb::QueryStats)` derives debug/clone/default/partial-eq.
- `get_query_num`, `add_query_num`, `add_query_stats`, `sub_query_stats`, `fill_query_stats`, `get_read_query_num`, `pop`, and `get_all_query_num`.
- `is_read_query` classifies `Get`, `Coprocessor`, and `Scan`.

## Control Flow
Setter/getter methods use match arms over `QueryKind`. Aggregate operations iterate `QUERY_KINDS`. `pop` swaps the inner protobuf with a default value, returning the previous stats and resetting the wrapper.

## State and Persistence Behavior
State is the wrapped protobuf counters. Operations mutate in memory only. `sub_query_stats` uses unsigned subtraction and assumes the left operand is greater or equal for each kind.

## Dependencies and Integration Points
Depends on `kvproto::pdpb`. It is re-exported by `store/mod.rs` for PD reporting and store query-stat aggregation.

## Risks
Unsigned subtraction can underflow in release builds if callers subtract larger counters. `Others` is intentionally ignored in most operations. Adding counters can overflow `u64` if used without bounds over very long intervals.

## Test Signals
No local tests in this file; behavior is deterministic match/iteration logic. Store module tests do not cover query stats.
