# sources/storage-engines/foundationdb/fdbserver/workloads/ConsistencyCheckUrgent.cpp

Purpose: Implements the `ConsistencyCheckUrgent` tester workload, a distributed shard-by-shard replica consistency check for caller-supplied `rangesToCheck`. Unlike the broader single-threaded consistency workload, this one prioritizes complete coverage, retry reporting, and failure propagation for urgent consistency checker tasks.

Important APIs/types/functions: `ConsistencyCheckUrgentWorkload`, `getKeyLocationsForRangeList`, `getVersion`, `checkDataConsistencyUrgent`, and `_start` drive the workload. It uses `krmGetRanges`, `keyServersPrefix`, `decodeKeyServersValue`, `serverTagKeys`, `serverListKeyFor`, `StorageServerInterface::getKeyValues`, `GetKeyValuesRequest`, `KeyRangeMap<bool>`, `IRateControl`, and version-vector helpers such as `addSSIdTagMapping` and `getLatestCommitVersion`.

Control flow: `start` logs the checker id and calls `_start`; `_start` exits for empty assignments, may mimic tester failure in simulation, then calls `checkDataConsistencyUrgent` at epoch 0. The check resolves shards intersecting requested ranges, decodes source storage servers, fetches interfaces, reads each shard chunk at a fresh read version from all source replicas, compares data and `more` flags against the first valid replica, rate-limits by reply bytes, and advances by last key until the shard is exhausted.

State and persistence behavior: The workload does not write application data. It reads system metadata and direct storage-server data, tracks failed ranges in memory, and recursively retries coalesced failed ranges until `CONSISTENCY_CHECK_URGENT_RETRY_DEPTH_MAX`. Persistent effects are limited to trace events; version-vector mode mutates the client-side SSID/tag cache on the `Database` object.

Dependencies/integration: It integrates tester assignment state (`rangesToCheck`, `sharedRandomNumber`), key-server metadata, server list metadata, storage RPCs, simulator failure injection, client/server knobs, and Flow actor retry semantics. It disables no background workloads itself, so callers must consider interference.

Risks: Direct storage RPC reads are sensitive to server removal, failed machines, version-vector metadata, backward-read settings, and transient `getKeyValues` failures. Inconsistencies are traced but do not immediately stop the shard loop; unavailable replies cause retry epochs. Retry depth exhaustion converts to `consistency_check_urgent_task_failed`.

Test signals: Key signals are `ConsistencyCheckUrgent_TesterStartTask`, shard complete/failed events, `ConsistencyCheck_DataInconsistent` with uniqueness/mismatch counts, retry-depth events, and final tester exit reason. A successful workload reaches `CompleteCheck`; validation failure is propagated by throwing urgent-task-failed.
