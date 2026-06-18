<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_info_accessor.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_region_info_accessor.rs

## Purpose
This file tests `RegionInfoAccessor` and raft engine region scanning. It verifies region range ordering, role reporting, split/merge updates, peer add/remove updates, leader transfer role changes, and `seek_region` behavior for raft engine backed stores.

## Important APIs, Types, and Functions
`dump` calls `RegionInfoAccessor::debug_dump` and checks the range index matches region metadata through `RangeKey::from_end_key`. `check_region_ranges` asserts ordered ranges. `test_region_info_accessor_impl` drives mutations. `test_node_cluster_region_info_accessor` registers an accessor through the coprocessor host. `test_raft_engine_seek_region` calls `raft_engine.seek_region`.

## Control Flow and Behavior
The accessor test writes keys, verifies the initial full-range region, splits at `k1`, `k4`, `k2`, and `k3`, checks ordered ranges, merges left-to-right and right-to-left, adds a peer, transfers leadership away from node 1, waits for `StateRole::Follower`, removes node 1's peer, and waits for the accessor to drop the removed region.

The raft-engine test splits at several keys, distributes leaders across stores, then seeks from key `b` on store 0's raft engine and expects regions `b`, `c`, and `d` with roles follower/leader/follower according to leader placement.

## State and Persistence
The test checks in-memory accessor state built from raftstore coprocessor updates and raft-engine persisted region metadata. It validates key ranges, peer lists, region epochs, and roles.

## Dependencies and Integration Points
It integrates `RegionInfoAccessor`, coprocessor host construction, PD split/merge/leader transfer, `tikv_kv::Engine`, and raft engine region iteration callbacks.

## Risks
Accessor updates are slightly asynchronous, so waits are needed after removal and leader transfer. Regressions include range index mismatch, stale role reporting, removed regions lingering, missing split/merge updates, and raft-engine `seek_region` returning wrong ordering or role data.

## Test Signals
Signals are exact ordered ranges, role transitions from leader to follower, expected peer membership, region count decrease after peer removal, and exact `seek_region` output from a start key.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_info_accessor.rs -->
