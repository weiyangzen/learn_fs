# sources/storage-engines/tikv/tests/integrations/server_encryption.rs

## Purpose
This file verifies encrypted snapshot transfer for both node and server cluster simulators. It ensures data from default, write, and lock column families survives learner addition and peer promotion when encryption is enabled.

## Important APIs, Types, and Functions
`test_snapshot_encryption<T: Simulator>` is the shared scenario. It calls `configure_for_encryption`, disables default PD operators, uses `run_conf_change`, `must_put`, `must_put_cf`, `must_add_peer`, `new_learner_peer`, `new_peer`, and `must_get_*_equal` helpers.

## Control Flow
The test enables encryption, writes ten keys into three CFs, adds store 2 first as learner and then as voter, writes an extra key to force replication progress, and checks that store 2 has representative default/lock/write CF values. Two test functions instantiate the scenario with `new_node_cluster` and `new_server_cluster`.

## State, Persistence, and Dependencies
Persistent state is cluster data and generated encrypted snapshot files under temporary paths. The tests call `take_path` before drop so cleanup order can occur after cluster shutdown.

## Integration Points, Risks, and Test Signals
The integration point is raft snapshot generation, encryption, transfer, ingestion, and CF-level retrieval. Signals are successful peer addition plus exact value reads on the target store. The scenario does not inspect encrypted bytes directly; it infers encryption compatibility from snapshot application success.
