# sources/storage-engines/tikv/components/snap_recovery/Cargo.toml

Purpose: manifest for the snapshot recovery component that exposes recovery-mode setup and gRPC recovery services.

Important APIs and dependencies: package `snap_recovery`, edition 2021. Default features enable test KV RocksDB and raft-engine backends through `tikv`. Dependencies include engine traits/Rocks, raft-log-engine, raftstore, PD client, grpcio, kvproto, encryption export, prometheus, tokio, futures, txn_types, and TiKV utilities.

Control flow and integration: the dependency set matches the crate responsibilities: open local engines, mutate config for recovery mode, serve `RecoverData` RPCs, inspect raft metadata, force leadership, wait apply, resolve MVCC data, and emit metrics.

State and persistence behavior: manifest only, but features select engine implementations that affect tests and local-engine service construction.

Risks: default test-engine features mean build/test behavior differs from production feature selection. Recovery code spans storage, raft, and PD, so dependency version drift can break broad contracts.

Test signals: crate tests live in source modules.
