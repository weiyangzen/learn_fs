# sources/storage-engines/tikv/components/snap_recovery/src/lib.rs

Purpose: crate root for snapshot recovery.

Important APIs: publicly exposes `init_cluster` and `services`, re-exports `enter_snap_recovery_mode`, `start_recovery`, and `RecoveryService`, imports TiKV logging macros, and keeps helper modules private: `data_resolver`, `leader_keeper`, `metrics`, and `region_meta_collector`.

Control flow, state, and integration: no direct runtime logic. The public surface is intentionally narrow: callers can enter recovery mode, start recovery bootstrap, and register/use the recovery gRPC service.

Risks: changing visibility affects external recovery orchestration. Private modules are tightly coupled to `services`.

Test signals: source module tests cover private logic.
