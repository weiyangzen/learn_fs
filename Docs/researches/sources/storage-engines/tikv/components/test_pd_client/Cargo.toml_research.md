# sources/storage-engines/tikv/components/test_pd_client/Cargo.toml

## Purpose
This manifest defines the private `test_pd_client` crate, an in-memory implementation of TiKV's `PdClient` trait used by raftstore and storage tests.

## Dependencies And Integration Points
Dependencies include `pd_client`, `kvproto`, `keys`, `raft`, `txn_types`, `tikv_util`, logging, failpoints, futures, grpcio error types, and `tokio-timer`. These match the crate's role as a fake PD client that generates IDs/TSOs, tracks regions/stores, emits heartbeat responses, and simulates scheduling operators.

## State, Persistence, And Risks
There is no disk persistence. Runtime state is all in memory inside `TestPdClient` and `PdCluster`. Because the crate implements a wide `PdClient` trait, it is sensitive to trait evolution in `pd_client`. Failpoint and timer dependencies allow tests to model asynchronous and failure behavior.

## Test Signals
Compile-time validation ensures the fake client still satisfies `PdClient`. Raftstore integration tests provide behavioral coverage for scheduling, bootstrap, split/merge, TSO, GC safe point, replication mode, unsafe recovery, and bucket reporting.
