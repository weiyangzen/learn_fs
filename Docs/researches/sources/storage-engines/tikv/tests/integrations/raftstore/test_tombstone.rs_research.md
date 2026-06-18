# sources/storage-engines/tikv/tests/integrations/raftstore/test_tombstone.rs

## Purpose
This file validates tombstone peer destruction, fast destroy cleanup, re-adding peers with new peer IDs, stale metadata recovery, safe tombstone GC behavior, and raft log cleanup when peers are destroyed.

## Important APIs, Types, and Functions
It uses `PeerState::Tombstone`, `RegionLocalState`, `StoreIdent`, `RaftMessage`, `CF_RAFT`, `CfNamesExt`, `Iterable`, `SyncMutable`, `RaftEngineDebug`, PD add/remove peer helpers, `IsolationFilterFactory`, `PartitionFilterFactory`, and raft log reads via `get_all_entries_to`.

## Control Flow
`test_tombstone` removes a peer, verifies only store ident and tombstone local state remain, sends a stale raft message, and expects `RegionNotFound`. `test_fast_destroy` removes a peer, injects dirty data while stopped, restarts and re-adds with a new peer ID, then ensures dirty data is removed. `test_readd_peer` isolates an old peer, removes and re-adds a new peer on the same store, and checks stale GC messages for the old peer are ignored. Other tests simulate stale local metadata before restart, unsafe tombstone GC scenarios, and log cleanup across destroy paths before and after log GC.

## State and Persistence Behavior
The file directly scans all CFs, decodes `StoreIdent` and `RegionLocalState`, writes artificial dirty data, and inspects raft log entries. It verifies peer destroy leaves a tombstone marker, removes user data and raft logs, preserves store identity, and does not let stale tombstone messages destroy a newly added peer.

## Dependencies and Integration Points
It integrates raftstore destroy-peer logic, PD conf change, raft message handling, stale peer GC, local engine CF scanning, raft engine debugging, log GC, and cluster restart/startup reconciliation.

## Risks
Incorrect tombstone handling can either leak removed-peer data and logs or delete data for a newly re-added peer. Stale metadata on restart and uninitialized tombstone messages are especially risky because they operate before normal raft membership stabilizes.

## Test Signals
Signals include exact remaining key count after destroy, tombstone state with expected conf version, `RegionNotFound` for tombstoned status requests, dirty data absence after re-add, live data presence after stale GC messages, and empty raft log entry lists after peer removal.
