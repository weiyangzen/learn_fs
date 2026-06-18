# sources/object-store/garage/src/model/garage.rs

## Purpose
This file constructs the full Garage model layer: configuration, metadata database, membership system, block manager, metadata tables, counters, lifecycle persistence, optional K2V subsystem, and background workers. It is the dependency injection root for model, S3, K2V, block, and table replication components.

## Important APIs, types, and functions
`Garage` owns config, background variables, replication factor, DB, `System`, `BlockManager`, admin/bucket/key tables, bucket mutation mutex, S3 object/MPU/version/block-ref tables, object/MPU counters, lifecycle persister, and optional `GarageK2V`. `Garage::new` performs initialization. `spawn_workers` starts block/table/counter/lifecycle/K2V/snapshot workers. `bucket_helper`, `key_helper`, and `locked_helper` expose helper APIs, with `locked_helper` acquiring the bucket/key mutation mutex. `GarageK2V::new` creates K2V counter, subscription manager, item table, and RPC handler.

## Control flow
Startup ensures metadata and data directories exist, opens the configured DB engine with fsync/cache/map-size options, decodes the 32-byte RPC network secret, parses replication mode, creates membership `System`, builds full-replication parameters for control tables and sharded replication parameters for data metadata, initializes the block manager, then creates all tables in dependency order. S3 tables are wired so object updates feed counters, MPU deletion, version deletion, block-ref deletion, and block refcount changes. K2V is conditionally initialized behind the `k2v` feature.

## State and persistence behavior
All metadata is persisted in the selected Garage DB under `metadata_dir`. Lifecycle worker state is persisted separately through `PersisterShared` named `lifecycle_worker_state`. The model registers a block refcount recalculation closure that scans `block_ref_table`. Auto snapshots are optional and configured by `metadata_auto_snapshot_interval`.

## Dependencies and integration points
This module integrates `garage_db`, `garage_rpc::system`, replication mode parsing, `garage_block::BlockManager`, `garage_table`, `garage_util::background`, config parsing, all model table modules, S3 tables, lifecycle worker, snapshots, and optional K2V RPC. Upper layers use `Garage` as the shared application state.

## Risks and edge cases
Initialization order matters because table update hooks reference other tables. Missing/invalid `rpc_secret`, invalid DB engine, or directory creation failure abort startup. The local `bucket_lock` does not coordinate bucket/key mutations across nodes, which is explicitly documented as a partial mitigation. Auto snapshot interval rejects values under 600 seconds. Feature-gated K2V changes the shape of `Garage` and bucket emptiness behavior.

## Test signals
No direct tests are in this file. Integration tests that start Garage nodes exercise it heavily. Focused tests should cover config error paths, table dependency wiring, worker spawning, snapshot interval validation, and K2V feature-enabled initialization.
