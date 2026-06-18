# sources/storage-engines/tikv/components/snap_recovery/src/init_cluster.rs

Purpose: prepares TiKV for snapshot recovery mode and updates local/PD cluster metadata before startup.

Important APIs and types: `enter_snap_recovery_mode` mutates `TikvConfig` for recovery. `start_recovery` opens local engines, updates local cluster id, fetches store id, and bootstraps PD using `bootcluster`. `LocalEngineService` abstracts local engine operations; `LocalEngines<EK, ER>` implements it. `create_local_engine_service` opens KV and raft engines based on config. `LOCK_FILE_ERROR` identifies running-process lock conflicts.

Control flow: recovery mode greatly extends election/stale/leader-missing timeouts, increases snapshot IO/concurrency/file-size settings, disables hibernate regions, disables prevote/check quorum, allows unsafe vote after start, disables RocksDB auto compactions, raises background jobs based on CPU quota, disables resolved-ts, increases raft client backoff, and disables practical region splitting by setting huge split thresholds. `bootcluster` constructs a PD store descriptor from server addresses, labels, binary path, timestamp, and git hash, allocates first region/peer IDs, then retries PD bootstrap up to 60 times while accepting an already-bootstrapped matching first region.

State and persistence behavior: `LocalEngines::set_cluster_id` reads and rewrites `STORE_IDENT_KEY`, then syncs KV. `create_local_engine_service` opens the actual data dir and raft dir/engine, including encryption manager setup. `handle_engine_error` exits gracefully and warns strongly on LOCK file conflicts.

Dependencies and integration points: integrates config, encryption export, Rocks engine factory, raft-log-engine, raftstore initial region, PD client, and TiKV server config. Used before normal TiKV startup in recovery workflows.

Risks: config changes are intentionally unsafe for normal operation and must be scoped to recovery. `get_store_id` unwraps missing store ident and can panic. PD bootstrap retry logs and sleeps synchronously. Opening live engines while TiKV is running is dangerous; LOCK file handling explicitly warns not to delete locks.

Test signals: no direct tests in this file; behavior is covered through recovery integration and engine-opening paths.
