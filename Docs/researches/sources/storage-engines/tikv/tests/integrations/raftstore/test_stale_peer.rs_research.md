# sources/storage-engines/tikv/tests/integrations/raftstore/test_stale_peer.rs

## Purpose
This file tests stale peer garbage collection, especially peers removed from region membership while isolated, uninitialized stale peers without data, stale learners, and stale peer cleanup after merge/restart.

## Important APIs, Types, and Functions
It uses `PeerState::Tombstone`, `RegionLocalState`, `CF_RAFT`, `PdClient` conf changes, `IsolationFilterFactory`, `RegionPacketFilter`, `MessageType::MsgSnapshot`, direct replica-read requests, and cluster helpers such as `must_remove_region`, `must_region_exist`, `must_region_not_exist`, `wait_destroy_and_clean`, and `configure_for_merge`.

## Control Flow
`test_stale_peer_out_of_region` isolates a peer, changes membership to a new set of peers, waits for the isolated peer to detect leader absence, and asserts it destroys itself. `test_stale_peer_without_data` creates an initialized peer that never receives snapshot data after split, isolates and removes it, and confirms only that stale region is tombstoned. Learner tests isolate learners, change conf versions or remove learners, then assert they are not prematurely deleted until PD validation or leader interaction marks them stale. The merge/restart test blocks snapshots for an added peer, removes it, restarts the node, and expects the uninitialized peer to be gone.

## State and Persistence Behavior
The file directly reads `RegionLocalState` from `CF_RAFT` and checks `PeerState::Tombstone`. It also checks user keys on affected and unaffected ranges to prove stale cleanup removes only the stale region data and preserves unrelated region data on the same store.

## Dependencies and Integration Points
It integrates raftstore stale-state checking intervals, PD validation, learner promotion/removal, split derivation mode, merge setup, snapshot filtering, and replica-read/read-index command paths.

## Risks
The covered risk is accidental data loss or stale peer survival. A stale peer that is not destroyed can disrupt future peer IDs or region routing; an overly aggressive cleanup can delete live data from another region. Timing knobs for leader-missing detection are critical to avoid flaky behavior.

## Test Signals
Signals include key absence after cleanup, unaffected key presence, tombstone local state, `must_region_not_exist` after restart, and successful destruction of stale learners only after the intended PD or leader interaction.
