# sources/storage-engines/tikv/src/server/raftkv2/node.rs

Purpose: owns raftstore-v2 node bootstrap and lifecycle. It initializes store metadata, bootstraps store identity in the raft engine, creates the v2 store batch system, bootstraps the first tablet/region when needed, registers the store in PD, initializes replication metadata, starts the store system, and shuts it down.

Important APIs/types/functions: `NodeV2<C, EK, ER>`; `new`; `try_bootstrap_store`; `start`; `start_store`; `load_all_stores`; `router`; `system`; `refresh_config_scheduler`; `stop`.

Control flow: `try_bootstrap_store` uses `Bootstrap::bootstrap_store`, sets store id, and creates `(StoreRouter, StoreSystem)`. `start` runs `bootstrap_first_region`; if it returns a region, it computes tablet path at `RAFT_INIT_LOG_INDEX` and opens the initial tablet. It then `put_store`s to PD, loads stores into replication state, and starts the store system exactly once.

State/persistence: durable bootstrap is raft-engine/tablet state. Runtime state is `system: Option`, `has_started`, logger, resource controller, and global replication mutex updates. It reuses legacy `init_store` for advertised store metadata.

Dependencies/integration: PD, `raftstore_v2::Bootstrap`, tablet registry/factory, v2 store system, transport, tablet snapshots, encryption key manager, importer, coprocessors, resource controller, and gRPC service manager. Risks include unwraps before bootstrap, TODO recovery after tablet open abort, PD failure panic, missing API-version check, and TODO dynamic config support.
