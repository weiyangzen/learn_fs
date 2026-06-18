<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_change_observer.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_region_change_observer.rs

## Purpose
This file tests the raftstore coprocessor `RegionChangeObserver` event stream for create, update, split, merge, destroy, removal, and re-addition of a region on a node.

## Important APIs, Types, and Functions
`TestObserver` implements `Coprocessor` and `RegionChangeObserver`, sending `(Region, RegionChangeEvent)` pairs through a synchronous channel from `on_region_changed`. `test_region_change_observer_impl` drives the scenario. It uses `BoxRegionChangeObserver`, `ObserverContext`, `RegionChangeReason`, `StateRole`, `post_create_coprocessor_host`, `find_peer`, and PD split/merge/conf-change helpers.

## Control Flow and Behavior
The test registers an observer only on node 1, starts a cluster, and verifies one initial `Create` event. It adds a peer and expects an `Update(ChangePeer)`, splits and accepts either order of `Update(Split)` and `Create`, merges and expects `Update(PrepareMerge)`, then `Update(CommitMerge)` plus `Destroy`. Finally it removes the node's peer, expecting update then destroy, re-adds the peer with a new peer ID, and expects create.

## State and Persistence
The observed region snapshots carry region IDs, key ranges, peer lists, and epochs. The test checks epochs change after update events and that destroy/create events reflect local membership changes.

## Dependencies and Integration Points
This is a coprocessor host integration test. It relies on raftstore event emission, PD operators, split/merge execution, local node observer registration, and `StateRole` delivery to the observer callback.

## Risks
Event ordering is intentionally flexible for split and commit-merge update/destroy pairs, but event cardinality is strict. Regressions include missing updates, stale epoch snapshots, duplicate observer registrations, and failing to destroy/recreate local observer state after peer removal.

## Test Signals
Signals are channel-received event variants, no extra channel messages after each phase, correct region IDs and range boundaries, expected peer counts, and the re-added peer ID `2333`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_change_observer.rs -->
