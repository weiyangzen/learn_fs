# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_truncate.c

## Purpose
`wtperf_truncate.c` implements the special wtperf truncate workload. It creates and consumes "truncate stones" so the table is periodically reduced to a target record count while insert activity may continue.

## Important APIs, Types, And Functions
Public functions are `setup_truncate`, `run_truncate`, and `cleanup_truncate_config`. Internal `decode_key` converts string keys to numeric positions. The file uses `TRUNCATE_CONFIG` and `TRUNCATE_QUEUE_ENTRY` from `wtperf.h`.

## Control Flow
`setup_truncate` opens the single benchmark table, finds first and last keys, computes a stone gap and needed stones from `truncate_count` and `truncate_pct`, and preloads the global stone queue when existing data is large enough. `run_truncate` updates expected total rows from summed inserts, adjusts a catch-up multiplier when behind, adds stones until the queue reaches the target, pops one stone, and either removes records one-by-one or calls `WT_SESSION.truncate` up to the stone cursor.

## State And Persistence Behavior
In-memory truncate state tracks expected table size, last key, catch-up multiplier, and queued stones. Persistent effects are deletes/truncates in the WiredTiger table. `cleanup_truncate_config` drains any remaining queue entries during `WTPERF` cleanup.

## Dependencies And Integration Points
The file integrates with the `worker` loop's truncate operation, key formatting from `generate_key`, operation counters from `sum_insert_ops`, and WiredTiger cursor/session truncate APIs. It assumes wtperf validation has restricted truncate to one table and one truncate worker.

## Risks
Queue state is stored in `WTPERF.stone_head`, so truncate is only safe under the single-thread invariant. Initial setup assumes the table has data and uses `testutil_check` on cursor navigation. Catch-up multiplier changes benchmark behavior dynamically and can create larger-than-expected truncate spans.

## Test Signals
Run truncate with both `truncate_single_ops=false` and true, verify validation rejects random-range or multi-table truncate, check table size trends toward `truncate_count`, and test cleanup of queued stones on early stop.
