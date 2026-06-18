# sources/storage-engines/tikv/tests/integrations/raftstore/test_transport.rs

## Purpose
This file tests raftstore transport behavior under network partitions and secure server connectivity.

## Important APIs, Types, and Functions
It uses `Cluster::partition`, `clear_send_filters`, `must_transfer_leader`, `must_put`, `must_get`, `leader_of_region`, `must_get_equal`, `new_node_cluster`, `new_server_cluster`, and `test_util::new_security_cfg`.

## Control Flow
`test_partition_write` starts a five-node cluster, writes a key, transfers leader to store 1, partitions either with the leader in a majority or in a minority, and verifies writes/read availability follow quorum rules. After healing, it resets leader cache, writes another key, and confirms the old leader catches up. `test_secure_connect` starts a secure server cluster and confirms replicated writes across all stores.

## State and Persistence Behavior
The tests observe replicated KV state on individual engines before, during, and after partitions. No direct raft log state is inspected; correctness is inferred from committed data and leader elections.

## Dependencies and Integration Points
The file integrates the test transport/filter layer, raft quorum/election behavior, server TLS/security configuration, and node/server cluster implementations.

## Risks
Partition handling regressions can allow minority writes, prevent majority progress, or fail to catch up healed peers. Secure transport regressions can break replication even when normal plaintext transport works.

## Test Signals
Signals include successful writes in majority partitions, leader movement away from the minority partition, changed value replication after healing, and all secure-cluster engines containing the written key.
