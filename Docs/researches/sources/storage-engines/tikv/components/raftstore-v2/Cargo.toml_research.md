# sources/storage-engines/tikv/components/raftstore-v2/Cargo.toml

Purpose: Defines the experimental/next-generation `raftstore-v2` crate, including default test-oriented features and the broad dependency set needed for multi-raft FSMs, tablets, workers, PD interaction, storage engines, and recovery.

Important APIs/types/functions: Default features enable `testexport`, RocksDB KV test engine support, and raft-engine raft test support. Additional feature groups cover failpoints, Rocks engine combinations, and panic test engines. Dependencies include `batch-system`, `engine_traits`, `pd_client`, `raftstore`, `raft`, `kvproto`, `sst_importer`, `resource_control`, `service`, `yatp`, and many TiKV support crates. Two integration test targets are declared: `raftstore-v2-failpoints` and `raftstore-v2-integrations`.

Control flow: Feature resolution determines test exports, failpoints, and engine backends. The crate code itself is organized in `lib.rs` into batch, bootstrap, FSM, operation, raft, router, and worker modules.

State and persistence behavior: Runtime state includes raft logs, region states, tablets, snapshots, and PD-reported metadata. Persistence is through engine trait implementations selected by tests or production integration, not by the manifest.

Dependencies and integration points: The manifest positions raftstore-v2 as a central integration crate spanning PD, storage engines, resource metering/control, gRPC service management, import SST, and asynchronous worker pools.

Risks: The default feature set is test-heavy; production consumers must be deliberate about feature selection. The git dependency on `yatp` master can create reproducibility risk if not locked. Large dependency surface increases compile and behavioral coupling.

Test signals: Declared failpoint and integration tests are the primary crate-level validation targets, requiring matching feature sets.
