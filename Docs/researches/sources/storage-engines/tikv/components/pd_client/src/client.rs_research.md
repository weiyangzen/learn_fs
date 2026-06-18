# sources/storage-engines/tikv/components/pd_client/src/client.rs

## Purpose
`client.rs` implements the original `RpcClient` for the `pd_client::PdClient` trait and `MetaStorageClient`. It owns cluster id, a reconnecting shared PD `Client`, and a monitor pool for periodic metadata refresh and TSO stream repair.

## Important APIs, Types, and Functions
- `RpcClient::new`/`new_async` validate PD endpoints, build a gRPC environment, create `Client`, spawn update and TSO-reconnect loops, and return a cluster-bound client.
- `header` creates PD request headers with the fixed cluster id.
- `get_region_and_leader` and `get_store_and_stats` are common async helpers.
- The `PdClient` impl covers cluster bootstrap/status, id allocation, store/region lookup, region and store heartbeats, split/scatter/report requests, GC safe point, TSO, service safe point updates, min resolved ts, bucket reports, RU metrics, and feature gate access.
- Stream senders for region heartbeat, bucket reports, and RU metrics lazily convert grpcio sinks into futures mpsc senders held under the inner client lock.
- The `MetaStorageClient` impl wraps get/put/delete/watch requests and fills meta-storage cluster id headers.

## Control Flow
Most unary requests build a protobuf request, set the PD header, create an executor closure over `Client`, issue grpcio async calls with current call options, check response headers, update histograms, and execute through `pd_client.request(..., retry).execute()`. Synchronous trait methods use `sync_request` or `block_on`. Periodic heartbeats often use `NO_RETRY`; leader-sensitive requests use `LEADER_CHANGE_RETRY`. Stream send paths initialize the stream on first use, enqueue messages to unbounded channels, and keep gauges for pending heartbeats/buckets.

## State and Persistence Behavior
The client stores immutable `cluster_id` plus mutable shared connection state inside `Client`. It does not persist data itself, but it drives persistent cluster state in PD: stores, regions, safe points, resource metrics, and meta-storage key/value operations. Feature gate state is updated from store heartbeat cluster version responses.

## Dependencies and Integration Points
It integrates with `kvproto` PD and meta-storage services, `security::SecurityManager`, `grpcio`, TiKV global timer, YATP monitor threads, metrics, failpoints, `txn_types::TimeStamp`, and the internal `util::Client` request/reconnect layer.

## Risks
Locking and stream initialization are delicate: grpc stream sender state transitions from `Either::Left` to `Either::Right` under write locks, and stream errors must trigger reconnects through the shared request machinery. Unbounded mpsc queues can accumulate if PD is slow. Some grpc async creation failures panic with `unwrap_or_else`, assuming local stub setup should not fail. `batch_load_regions` unwraps `scan_regions`, so PD scan failures panic there.

## Test Signals
This file contains failpoint hooks for heartbeat send failure and meta-storage get rejection. Broader behavior is usually covered by integration tests with mock/real PD clients, metrics assertions, and callers exercising safe point, TSO, heartbeat, and stream reconnect paths.
