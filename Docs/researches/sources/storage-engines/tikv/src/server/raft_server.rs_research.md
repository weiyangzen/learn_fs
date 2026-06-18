# sources/storage-engines/tikv/src/server/raft_server.rs

Purpose: owns legacy raftstore node bootstrap and lifecycle through `MultiRaftServer<C, EK, ER>`. It turns server config into a PD-visible `metapb::Store`, verifies or creates the on-disk store identity, prepares/bootstraps the first region, registers the store in PD, initializes replication-mode metadata, and starts/stops the raftstore batch system.

Important APIs/types/functions: `init_store`; `MultiRaftServer::{new, try_bootstrap_store, start, stop}`; `check_store`; `check_api_version`; `prepare_bootstrap_cluster`; `bootstrap_cluster`; `start_store`; router/scheduler accessors.

Control flow: startup reads `STORE_IDENT_KEY`; missing identity allocates a PD store id and writes store identity. Cluster bootstrap reuses `PREPARE_BOOTSTRAP_KEY` when present, otherwise checks PD cluster bootstrap state, allocates first region/peer ids, writes prepared metadata, retries PD bootstrap up to 60 times, and clears prepared keys according to the winning first region. The store is put to PD only after the cluster is bootstrapped, then raftstore is spawned.

State/persistence: persistent engine state is store ident, prepared bootstrap key, and raftstore bootstrap metadata. API-version switching persists a new `StoreIdent` after scanning data CFs for incompatible non-TiDB keys. Runtime state includes `has_started`, `store_meta.store_id`, `GlobalReplicationState`, background worker, health controller, and `RaftBatchSystem`.

Dependencies/integration: PD allocation/bootstrap/store registration, raftstore batch system, split/check workers, importer, snapshots, coprocessors, causal ts, disk checker, gRPC service manager, resource metering, and health. Risks include PD failure panic in `load_all_stores`, blocking bootstrap retries, expensive API-version scans, and unwrap/expect reliance on bootstrap invariants. Test signals are mainly failpoints and integration tests.
