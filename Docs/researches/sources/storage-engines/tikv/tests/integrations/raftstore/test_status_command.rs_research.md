# sources/storage-engines/tikv/tests/integrations/raftstore/test_status_command.rs

## Purpose
This file tests raftstore status/control-plane commands for region detail and latency inspection in both raftstore v1 and v2 router paths.

## Important APIs, Types, and Functions
It uses `cluster.region_detail`, `LatencyInspector`, `InspectFactor::{RaftDisk,KvDisk}`, `StoreMsgV1::LatencyInspect`, `StoreMsgV2::LatencyInspect`, and router `send_control`. It imports both `test_raftstore::Simulator` and `test_raftstore_v2::Simulator` traits to exercise both implementations.

## Control Flow
`test_region_detail` starts a five-node server cluster and checks that region detail for region 1 contains region metadata, full peer list, initial epoch, and current leader. `test_latency_inspect` starts a v1 node cluster with async store IO pool and a v2 node cluster, sends latency inspection control messages, and waits for callback durations. `test_sync_latency_inspect` repeats the v1 path with `store_io_pool_size = 0` to exercise synchronous inspection.

## State and Persistence Behavior
No direct persistence is inspected. The region detail test observes in-memory raftstore region metadata and leader state; latency tests validate control-message execution and timing callback delivery.

## Dependencies and Integration Points
The file integrates health controller latency inspection, raftstore/v2 control routers, store IO pool configuration, and cluster metadata/status APIs.

## Risks
Status paths are often used by diagnostics and health controllers; regressions may not affect normal reads/writes but can break observability or health decisions. The tests depend on callbacks firing within two seconds.

## Test Signals
Signals are exact region metadata assertions and successful receipt of latency inspection callback durations for raft and kv disk factors in v1 and for the v2 router path.
