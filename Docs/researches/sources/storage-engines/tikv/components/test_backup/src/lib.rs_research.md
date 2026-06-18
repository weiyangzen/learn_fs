# sources/storage-engines/tikv/components/test_backup/src/lib.rs

## Purpose
This file exports the primary backup test harness for TiKV. `TestSuite` creates a multi-node server cluster, starts backup endpoints for each node, exposes convenience write/read APIs, schedules backup tasks, and computes reference checksums for both transactional and raw KV data.

## Important APIs, Types, And Functions
`TestSuite` contains the server cluster, one lazy backup worker per store, a TiKV gRPC client bound to the region leader, an RPC `Context`, timestamp state, a shared background worker, and the active `ApiVersion`. `new` builds a server cluster with the requested API version, configures lease-read timing, starts backup endpoints using `backup::Endpoint::new`, writes a bootstrap key, discovers leader context, and creates a `TikvClient`.

Mutation helpers include `alloc_ts`, `must_raw_put`, `must_raw_get`, `must_kv_prewrite`, `must_kv_commit`, and `must_kv_put`. Backup scheduling helpers are `backup` for MVCC backup and `backup_raw` for raw backup; both build `BackupRequest`s against a local external storage backend and schedule a `Task` on every endpoint. Validation helpers include `admin_checksum`, `raw_kv_checksum`, and `storage_raw_checksum`. `name_to_cf` decodes SST CF from file names, and `make_unique_dir` creates random subdirectories.

## Control Flow And State
The suite is cluster-backed and mutable. Timestamp allocation increments local `TimeStamp`; transactional writes perform prewrite and commit RPCs with retries; raw operations adjust `Context` API version for V1ttl compatibility and use TTL according to destination API version. Backups fan out identical requests to every backup endpoint and return a futures channel receiver for collecting `BackupResponse`s.

## Persistence And Integration Points
The harness integrates with raftstore clusters, TiKV storage snapshots, backup workers, local external storage, raw/TiKV RPCs, coprocessor checksum logic, and API-version raw-value encoding. Persistent state lives in the test cluster engines and in local backup target directories.

## Risks And Test Signals
The `retry_req!` macro uses both retry count and elapsed-time conditions; long CI delays or leader changes can affect behavior. Raw checksum scanning uses internal data-key iteration and must respect CF and upper-bound encoding. `admin_checksum` scans through `SnapshotStore` and `RangesScanner`, making it a strong reference for backup results. Assertions in `must_*` methods fail fast on region errors or RPC errors.
