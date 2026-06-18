# sources/storage-engines/tikv/tests/integrations/raftstore/test_stats.rs

## Purpose
This file validates store heartbeat stats, hotspot reporting, query statistics, auto-split trigger evidence, and read/write query accounting for raw KV, transactional KV, batch commands, coprocessor, pessimistic lock, rollback, and delete-range paths.

## Important APIs, Types, and Functions
It uses `TikvClient`, `RawGetRequest`, `GetRequest`, scan/batch variants, `BatchCommandsRequest`, transactional prewrite/commit/pessimistic-lock/rollback requests, `QueryKind`, `QueryStats`, PD store stats/hotspot APIs, `DagSelect`, `ProductTable`, and API-version helpers `KvFormat` / `test_kv_format_impl`. Local helpers include `check_available`, `test_query_num`, `check_query_num_read`, `check_query_num_write`, `check_split_key`, `raw_put`, `put`, and `batch_commands`.

## Control Flow
Store stats tests reduce heartbeat intervals, split a region, flush engines, and wait for PD to observe region count and available-space changes. Hotspot tests force failpoints for low thresholds and collect read stats. Query-stat templates build closures for raw and txn operations, configure request source and API version, issue a read/write workload, then poll PD stats for expected query counts and split-key evidence. Batch command tests stream 100 batches of 10 requests and wait for 1000 responses before forcing metrics flush with scans.

## State and Persistence Behavior
The tests persist KV data through raw and txn paths, flush RocksDB CFs, and use PD mock state as the primary observable persistence of stats. Transactional tests allocate TSO timestamps, prewrite/commit mutations, acquire pessimistic locks, and perform rollback/delete-range requests.

## Dependencies and Integration Points
The file integrates raftstore store-heartbeat reporting, PD hotspot collection, split controller QPS thresholds, request-source tagging, gRPC unary and streaming batch APIs, API v1/v2/raw encoding, coprocessor request source propagation, and failpoints: `mock_hotspot_threshold`, `mock_tick_interval`, `mock_collect_tick_interval`, and `only_check_source_task_name`.

## Risks
The primary risk is silent observability regression: requests may still succeed while query stats, hotspots, request sources, or split keys are not reported correctly. Failpoint and timing dependence can make the tests brittle. API encoding differences are also risky because split-key checks must compare encoded raw or txn keys correctly.

## Test Signals
Signals include PD region count, changed available size, nonzero hotspot read keys/bytes, exact or minimum query counts by `QueryKind`, successful split-key lookup after auto split, no region errors for write paths, and full batch-command response counts.
