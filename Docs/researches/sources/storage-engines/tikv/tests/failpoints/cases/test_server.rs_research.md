# sources/storage-engines/tikv/tests/failpoints/cases/test_server.rs

## Purpose
This file tests TiKV server-side raft transport and health behavior under failpoint-induced failures: store-id/address mismatch, full raft send channels, health-service status transitions, and raft message observer rejection. It verifies server behavior around connection recovery and status reporting rather than storage semantics.

## Important APIs, Types, And Functions
The tests use `new_server_cluster`, `cluster.run_node`, `cluster.stop_node`, PD `get_store`, `must_put`, `async_put`, and engine assertions. Raft transport is exercised with `RegionPacketFilter`, `CloneFilterFactory`, and `MessageType` filters. Health checks build a grpc health service from `health_controller.get_grpc_health_service()` using `grpcio::ServerBuilder`, `HealthClient`, and `HealthCheckRequest`. Failpoints include `mock_store_refresh_interval_secs`, `send_raft_message_full`, `on_batch_raft_stream_drop_by_err`, `pause_on_peer_collect_message`, `force_reject_raft_append_message`, and `force_reject_raft_snapshot_message`.

## Control Flow
`test_mismatch_store_node` swaps node addresses by stopping nodes, restarting node 2 on node 3's address and node 3 on node 2's address, and blocking prevote traffic. With store refresh forced to zero interval, a write should trigger address refresh and recover replication despite the original mismatch. `test_send_raft_channel_full` injects a full send channel and asserts this condition should not drop the batch raft stream, then removes the failpoint and confirms replication resumes.

`test_serving_status` starts a standalone grpc health server around TiKV's health controller. It observes normal `Serving`, explicit `NotServing`, `ServiceUnknown` while peer collection is paused long enough to make raftstore progress unobservable, and recovery back to `Serving` after the failpoint is removed. `test_raft_message_observer` rejects append and snapshot messages while adding peers, validates peers do not receive data while rejection is active, then removes failpoints and verifies both existing and newly added peers catch up.

## State And Persistence Behavior
Persistent state is ordinary replicated KV data in the engines. Transient server state includes PD store address metadata, raft client connection/cache state, bounded raft send queues, health controller serving flags, and raftstore progress collection. The tests check that transient transport failures do not corrupt durable data and that recovery leads to replicated KV state on all expected stores.

## Dependencies And Integration Points
The suite connects test raftstore cluster orchestration, PD store metadata, grpc transport, batch raft streams, health checking, raft message observers, and TiKV failpoints. It also depends on `tikv_util::HandyRwLock` to access simulator internals for health controllers.

## Risks And Edge Cases
Risks covered include a raft client keeping a stale address after a store-id mismatch, treating send-channel backpressure as a stream-breaking error, health status remaining `Serving` while peer collection is stuck, health status ignoring manual serving toggles, and raft observer rejection leaving peers permanently unable to catch up.

## Test Signals
Assertions check address metadata after refresh, replicated values on affected engines, no panic on stream-drop failpoint while the send channel is full, grpc health status transitions, absent data while append/snapshot rejection is active, and successful replication after failpoints are removed.
