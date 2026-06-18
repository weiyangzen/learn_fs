# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/store.rs

## Purpose
This file implements raftstore-v2 PD store-heartbeat handling on `Runner<EK, ER, T>`. It builds `pdpb::StoreStats`, filters and caps per-region hotspot read statistics, records disk/engine/query/slowness metadata, sends store heartbeats to PD, and applies selected PD heartbeat responses such as unsafe recovery plans and gRPC pause/resume control. It also supports fake store heartbeats when normal heartbeat scheduling is delayed by local slowness.

## Important APIs, Types, and Functions
- `StoreStat` is the runner-owned aggregate state for store heartbeat deltas. It tracks cumulative read bytes/keys/query counts, last reported counters, last report timestamp, local histograms for region read/write bytes/keys, and recorded CPU/read-IO/write-IO metrics.
- `hotspot_*_report_threshold()` centralize read hotspot thresholds for keys, bytes, query count, and CPU usage. The `mock_hotspot_threshold` failpoint can force threshold zero for tests.
- `PeerCmpReadStat` is a small ordering wrapper used with `TopN` to select peer stats by metric.
- `collect_report_read_peer_stats()` sends all peer stats when the candidate map is modest; otherwise it includes the top regions by read keys, read bytes, read query count, and unified-read CPU usage, with duplicate regions removed by map deletion.
- `get_read_query_num()` maps PD query stats to the read-query sum used for ranking.
- `Runner::handle_store_heartbeat()` is the core path. It computes deltas since `last_report_ts`, fills capacity/used/available, flushes local histograms, updates slowness, marks stopping state, calls `pd_client.store_heartbeat`, and asynchronously processes PD response actions.
- `Runner::handle_fake_store_heartbeat()` constructs a busy heartbeat with store id, region count, snapshot counts, and snapshot traffic gauges, then calls the normal heartbeat path with `is_fake_hb = true`.
- `Runner::is_store_heartbeat_delayed()` decides whether delayed heartbeat reporting should synthesize a fake heartbeat, bounded by `STORE_HEARTBEAT_DELAY_LIMIT`.
- `Runner::handle_inspect_latency()` forwards latency inspection to the store control router.
- `Runner::handle_update_store_infos()` refreshes store-level CPU and IO metric samples.
- `collect_engine_size()` reads disk capacity/used/available, with a testexport branch that resets global disk stat mocks from current path stats.

## Control Flow
Normal heartbeat collection walks `self.region_peers`, computes each peer's deltas from last store report counters, subtracts last query stats, converts accumulated CPU milliseconds to an interval percentage, clears orphan CPU records, and skips regions below all hotspot thresholds. Qualified regions become `pdpb::PeerStat` entries, then `collect_report_read_peer_stats()` caps the payload. Store-level stats are enriched with disk size, total read deltas, query deltas, CPU/IO samples, gRPC pause status, interval start, slowness metadata, and stopping state before being sent to PD.

The PD response future handles unsafe recovery first. Force-leader plans build a failed-store set and send `enter_force_leader` messages through an `UnsafeRecoveryRouter`. Other plans send create, destroy, and demote messages with an execute-plan syncer. Awaken regions are logged and ignored because raftstore-v2 has no hibernated regions. `control_grpc` responses call `GrpcServiceManager::pause` or `resume`.

Fake heartbeats reuse the normal heartbeat construction but deliberately do not advance `last_report_ts`, so a busy/slowness report does not make the node appear normally scheduled.

## State and Persistence Behavior
The file does not directly persist raft data. It mutates in-memory heartbeat accounting on the runner: last read counters, last query counts, last report timestamp, store metrics, and per-peer last store-report counters. It reports persistent storage capacity through global disk stats and PD `StoreStats`. It also triggers persistent recovery-related actions indirectly by routing unsafe recovery plans to raftstore control paths. Histogram flushing is important because metrics are local collectors.

## Dependencies and Integration Points
It integrates with `pd_client::PdClient` and `kvproto::pdpb` for store heartbeat RPCs, `raftstore::store` unsafe recovery syncers and snapshot metrics, `health_controller::LatencyInspector`, `tikv_util` disk/time/topn/query stats helpers, and raftstore-v2 `StoreMsg`/`UnsafeRecoveryRouter`. Failpoint hooks support hotspot threshold testing. PD heartbeat tests in this subset exercise the fake-heartbeat path.

## Risks and Edge Cases
- Hotspot filtering depends on unsigned deltas from monotonically increasing counters; any counter reset before the last-report fields are reset can underflow.
- Fake heartbeats intentionally leave `last_report_ts` unchanged; callers must avoid repeated fake reports outside the delay guard.
- Unsafe recovery response handling is asynchronous and logs send failures, so later recovery syncer behavior must handle partial routing failures.
- Top-N selection can report up to four dimensions of `HOTSPOT_REPORT_CAPACITY`, not a strict 1000 total, because each metric contributes independently.
- Disk stat mocking in testexport builds changes global disk metrics and can affect tests that share process state.

## Test Signals
`tests/failpoints/test_pd_heartbeat.rs` forces small tick intervals and slowness failpoints to validate fake store heartbeat behavior. `tests/integrations/test_pd_heartbeat.rs` validates normal store heartbeat stats, region leader reporting, and bucket reporting. The hotspot threshold failpoint indicates tests can force peer-stat emission when validating PD payloads elsewhere.
