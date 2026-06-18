# sources/storage-engines/tikv/components/test_pd_client/src/pd.rs

## Purpose
This file implements `TestPdClient`, a rich in-memory implementation of TiKV's `PdClient` trait. It models PD cluster metadata, stores, regions, leaders, operators, heartbeats, TSO allocation, GC safe points, replication status, bucket reports, and unsafe recovery hooks for raftstore and storage tests.

## Important APIs, Types, And Functions
Top-level helpers build PD heartbeat responses: `new_pd_change_peer`, `new_pd_change_peer_v2`, `new_split_region`, `new_pd_transfer_leader`, `new_pd_merge_region`, and `new_pd_batch_switch_witnesses`. `SchedulePolicy` controls operator repetition. `Operator` variants represent add/remove peer, transfer leader, merge, split, leave joint, joint conf change, and witness switching. `Operator::make_region_heartbeat_response` converts pending operators into PD responses, while `try_finished` checks observed region/leader state to decide whether to continue.

`PdCluster` stores all mutable metadata: cluster config, stores with heartbeat channels, regions indexed by encoded end key and ID, region stats, operators, leaders, down/pending peers, bootstrap flag, GC/min resolved timestamps, replication status, unsafe recovery reports/plans, and bucket stats. Its methods bootstrap the cluster, allocate IDs, manage stores/regions, validate stale epochs and overlaps, process heartbeats, poll scheduled heartbeat responses, and handle store heartbeat recovery plans.

`TestPdClient` wraps `PdCluster` in `Arc<RwLock<_>>`, owns timer and failure flags, TSO counter, feature gate, and service safe points. It provides many test convenience methods such as `must_add_peer`, `must_remove_peer`, `must_split_region`, `must_merge`, `transfer_leader`, `joint_confchange`, `switch_witnesses`, replication-mode configuration, TSO manipulation, and unsafe-recovery plan/report access.

## Control Flow And State
Cluster state changes mostly through `PdClient` trait methods and explicit test helpers. Bootstrap seeds the first store and region. Region heartbeats validate epochs/overlaps, update leaders and stats, and send scheduled operator responses to the leader store's channel. `handle_region_heartbeat_response` combines direct queued responses with periodic polling every 500 ms, so operators can be resent until observed as complete. TSO allocation is atomic and handles logical overflow by advancing physical time.

## Persistence And Integration Points
All state is in-memory. The client integrates with TiKV's `PdClient` trait, raft protobuf conf changes, region/store protobufs, key encoding helpers, failpoints, global timer handle, feature gates, and raftstore utility functions for peer lookup and key-in-region checks.

## Risks And Test Signals
This is a broad fake PD, not a full PD. Epoch/overlap checks approximate stale-region handling; default max-peer scheduling can add/remove peers automatically unless disabled; many `must_*` helpers spin up to 500 times with 10 ms sleeps. `set_tso` panics if asked to decrease time. `trigger_tso_failure` and failpoints model transient failures. Tests validate behavior through convenience assertions, heartbeat-response streams, region counts, leader checks, split/merge completion, store stats, bucket merges, service safe point records, and unsafe-recovery report/plan exchange.
