<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_prevote.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_prevote.rs

## Purpose
This file validates raft prevote behavior after partitions, reboots, isolated followers, peer creation, and stale minority removal. It ensures prevote prevents disruptive term increases while still allowing legitimate elections and peer bootstrap traffic.

## Important APIs, Types, and Functions
`FailureType` models partition or reboot failures. `attach_prevote_notifiers` installs `MessageTypeNotifier`s for `MsgRequestPreVote` and `MsgRequestPreVoteResponse`. `test_prevote` is the shared scenario driver. Additional helpers are `test_pair_isolated`, `test_isolated_follower_leader_does_not_change`, and `test_create_peer_from_pre_vote`.

## Control Flow and Behavior
The shared prevote driver enables `prevote`, disables hibernate regions for observability, configures lease-read/election timing, transfers leadership, optionally attaches notifiers, applies a partition or reboot, checks whether prevote messages were observed, recovers the cluster, and verifies writes still succeed.

Other tests isolate a minority and let PD remove those peers, verify an isolated follower does not increase term or change the leader after reconnect, and verify a new peer can be created from prevote-triggered communication after isolation is cleared.

## State and Persistence
The file observes raft message traffic, leader identity, term stability through status requests, peer removal, and key persistence across failure/recovery. It does not directly inspect on-disk state, but it depends on raftstore persisting enough membership and term information to recover safely.

## Dependencies and Integration Points
It uses raft message filters, PD remove/add peer operations, `new_status_request`, leader commands, cluster partition/reboot controls, and `HandyRwLock` access to simulator internals.

## Risks
Prevote behavior is time-sensitive. Tests can miss messages if elections are slow or hibernation suppresses traffic, hence the explicit timing configuration. Regressions include unnecessary term bumps, leader churn after reconnect, isolated minority peers failing to remove themselves, or new peers not bootstrapping from prevote traffic.

## Test Signals
Signals are notifier channel delivery or timeout, stable leader and term after isolation, successful post-recovery writes, removed regions on isolated peers, and replicated data on newly added peers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_prevote.rs -->
