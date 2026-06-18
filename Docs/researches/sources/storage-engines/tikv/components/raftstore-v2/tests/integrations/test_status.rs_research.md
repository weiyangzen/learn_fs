# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_status.rs

## Purpose
This file validates basic raftstore-v2 status query behavior for region leader and region detail commands, including invalid store-id rejection.

## Important APIs, Types, and Functions
- `test_status()` builds `RaftCmdRequest` status requests with `StatusCmdType::RegionLeader` and `StatusCmdType::RegionDetail`.
- It uses `new_peer(1, 3)` as the initial single-node leader peer expectation.

## Control Flow
The test queries region 2 for leader, then region detail. It verifies leader, region id, empty range bounds, peer list, and initial epoch version/conf version. It mutates the header peer store id to 4 and expects a store-not-match error.

## State and Persistence Behavior
No persistent data is modified. The file observes bootstrapped region metadata and leader state.

## Dependencies and Integration Points
It uses the shared cluster query helper, raft command status protobufs, and raftstore-v2 status query path.

## Risks and Edge Cases
- Status queries still need header validation; wrong store id should not return local metadata.
- Initial region detail must match bootstrap constants for single-node raftstore-v2.

## Test Signals
Signals include exact leader peer, region id 2, empty start/end keys, single peer, epoch `(version=1, conf_ver=1)`, and `store_not_match` error.
