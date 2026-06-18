# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_pd_heartbeat.rs

## Purpose
This test validates fake store-heartbeat reporting when normal heartbeat scheduling is perceived as delayed or blocked by slowness. It specifically targets `worker/pd/store.rs` fake heartbeat behavior.

## Important APIs, Types, and Functions
- `test_fake_store_heartbeat()` builds a cluster with very short PD store-heartbeat and inspect intervals.
- Failpoint `mock_collect_tick_interval` makes collection interval immediate; `mock_slowness_last_tick_unfinished` simulates unfinished slowness inspection.
- It sends `StoreMsg::Tick(StoreTick::PdStoreHeartbeat)` and reads PD store stats through `PdClient::get_store_stats_async`.

## Control Flow
The test sends an explicit store heartbeat and records PD stats, then enables the slowness failpoint and waits long enough for fake heartbeat logic to run. It fetches store stats again and checks capacity/used size. If PD reports `start_time == 0`, the stats are interpreted as a fake heartbeat and must be marked busy; otherwise normal heartbeat stats must not be busy.

## State and Persistence Behavior
No raft data is persisted. The observable state is PD's in-memory/test-server store stats. The test confirms fake heartbeat contents reuse real disk stats but do not report writes.

## Dependencies and Integration Points
It integrates the store control router tick path, PD client/test server, heartbeat intervals in store config, and slowness failpoints used by the raftstore-v2 inspect path.

## Risks and Edge Cases
- Fake heartbeat must report enough store identity/capacity data for PD to mark the store busy, not missing.
- Normal heartbeats and fake heartbeats can race; the test handles both by checking `start_time`.
- Failpoints are removed explicitly to avoid contaminating other failpoint tests.

## Test Signals
Expected signals are nonzero capacity and used size, zero keys written, and `is_busy` true only for fake heartbeat stats.
