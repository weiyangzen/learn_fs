# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_pd_heartbeat.rs

## Purpose
This integration file validates raftstore-v2 PD reporting for region leaders, store heartbeat statistics, and region bucket reporting/refreshing.

## Important APIs, Types, and Functions
- `test_region_heartbeat()` queries local region leader status and then polls PD for region leader by id.
- `test_store_heartbeat()` writes a key, sends a PD store-heartbeat tick, and validates PD store stats for capacity/used size, keys written, and bytes written.
- `test_report_buckets()` enables coprocessor region buckets, writes enough data, flushes, triggers split-region check and report-buckets ticks, validates bucket stats in PD, then refreshes bucket ranges and confirms merged bucket stats reset.

## Control Flow
Tests build request headers/status requests manually or through router helpers. Store heartbeat uses `StoreMsg::Tick(StoreTick::PdStoreHeartbeat)`. Bucket reporting writes repeated padded keys, flushes default CF to make split-key detection possible, sends `PeerTick::SplitRegionCheck` and `PeerTick::ReportBuckets`, then uses PD client bucket APIs. It also sends `PeerMsg::RefreshRegionBuckets` with bucket ranges to test local bucket merge before another report.

## State and Persistence Behavior
Store stats and bucket stats are observed in PD's test server. Bucket tests also mutate tablet data, flush it, update in-memory/local bucket metadata, and reset per-bucket write stats after reporting.

## Dependencies and Integration Points
The file integrates router status queries, PD client APIs, store control ticks, peer ticks, coprocessor bucket config, `ReadableSize`, `SimpleWriteEncoder`, and tablet registry flush.

## Risks and Edge Cases
- Store heartbeat byte counts must exceed encoded write payload size and key counts must reset per interval.
- Bucket stats must be reported once and then reset to zero on the next report.
- Refreshing same bucket ranges twice must merge bucket metadata into a single range without corrupting PD report shape.
- Tests account for initial PD stats possibly having `start_time == 0`.

## Test Signals
Signals include PD leader lookup, nonzero capacity/used, exact key count, bytes-written lower bound, bucket key count > 2, per-bucket write stats bounds, zeroed stats on second report, and single merged bucket stat vector after refresh.
