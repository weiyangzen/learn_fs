# sources/storage-engines/tikv/tests/integrations/raftstore/test_joint_consensus.rs

Purpose: tests raft joint consensus configuration changes, including multi-peer changes, entering/leaving joint state, serving requests while joint, peer replacement, invalid request rejection, restart persistence, and leader election while joint.

Important APIs and functions: `call_conf_change_v2`, `call_conf_change`, `leave_joint`, `change_peer`, `put_request`, and `must_has_peer` wrap raft admin commands and role assertions. Tests use PD helpers `must_joint_confchange`, `must_leave_joint`, and `is_in_joint`, along with raft `ConfChangeType` and peer roles including learner/demoting voter.

Control flow: tests create node clusters, disable default PD operators, run initial conf change, then apply joint changes with multiple add/remove/promote/demote operations. Request-in-joint tests isolate old or new configuration peers to assert both configurations need quorum. Invalid request tests submit malformed joint changes and expect specific errors. Restart tests stop/start the leader while joint, then ensure state persists.

State and persistence: verifies PD region peer roles, engine key presence/absence on stores, joint-state flags, leader peer roles, split/merge restrictions, and role state after leaving joint. Restart coverage ensures joint config survives node restart.

Dependencies and integration points: integrates raftstore joint consensus implementation, PD test client commands, raft admin command encoding, isolation filters, `block_on_timeout`, and direct engine key reads.

Risks: expected error substrings are policy-coupled. Joint consensus correctness depends on both old and new quorum semantics; tests cover representative but not exhaustive topology changes. Some helper requests hard-code peer ids matching store ids.

Test signals: multi-change requests replicate data to new peers and remove old peers, normal writes obey joint quorum, invalid changes return targeted errors, merge is rejected in joint state, joint state persists across restart, and both old/new configuration peers can become leaders when valid.
