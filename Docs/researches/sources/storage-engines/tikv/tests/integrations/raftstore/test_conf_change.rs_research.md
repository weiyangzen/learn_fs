# sources/storage-engines/tikv/tests/integrations/raftstore/test_conf_change.rs

Purpose: broad raftstore membership-change suite covering add/remove peers, learner promotion, PD-driven replica adjustment, split-brain prevention, safety checks under partial failure, leader transfer constraints, stale peer cleanup, snapshot-based learner catchup, and partition removal rules across raftstore v1/v2 node/server clusters.

Important APIs and functions: `call_conf_change!` builds admin conf-change requests with the current PD epoch. `new_conf_change_peer`, `wait_till_reach_count`, and `find_leader_response_header!` support repeated scenarios. Tests use PD helpers such as `must_add_peer`, `must_remove_peer`, `must_joint_confchange`, `must_none_peer`, `region_leader_must_be`, and direct cluster operations for isolation, partition, transfer leader, async remove, and snapshot filters.

Control flow: most tests start from a one-peer region via `run_conf_change`, disable PD default operators, add peers/learners, write keys to force replication or snapshots, then remove/promote/transfer under controlled network conditions. Safety tests stop or isolate leaders/followers to verify unsafe additions/removals are rejected. Slow snapshot tests install a custom filter that drops snapshot messages until pending-peer state is observed, then clears it and verifies promotion.

State and persistence: verifies engine key presence/absence after peer add/remove, PD region peer lists and pending peers, `RegionLocalState` tombstone after self-removal, leader records, stale peer data cleanup, and snapshot-applied data. Partition tests depend on persistent raft logs and peer metadata to prevent old configurations from serving.

Dependencies and integration points: integrates `test_pd_client`, raft admin commands, raft message filters, PD scheduling/operator behavior, learner role helpers, `test_raftstore_macro::test_case`, v1/v2 clusters, and RocksDB engine reads.

Risks: many tests rely on sleeps, polling, and simulated network filters. Default PD operator state must be explicitly controlled. Safety semantics are tightly coupled to raftstore policy, so legitimate policy changes may require updating expected error strings or peer-count behavior.

Test signals: replicated keys appear only on active peers, removed peers lose data or report region not found, duplicate peer operations return errors, unsafe conf changes are rejected while safe ones proceed, learner pending/promoted states transition correctly, stale peers self-destroy, and operations complete faster than heartbeat-only paths in the fast-conf-change test.
