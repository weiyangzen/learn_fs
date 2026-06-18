# sources/storage-engines/tikv/components/backup-stream/tests/suite.rs

## Purpose
This file is the shared integration-test harness for backup-stream tests. It builds simulated TiKV clusters, starts backup-stream observers/endpoints and gRPC log-backup services, provides metadata-store error injection, writes transactional test data, forces flushes, computes checkpoint views, verifies flushed backup files, and wraps KV client operations with assertions.

## Important APIs, Types, And Functions
`SuiteBuilder` configures test name, node count, metadata-store error injection, backup-stream config mutation, and cluster config mutation. `Suite` owns endpoint workers, the `ErrorStore<SlashEtcStore>`, cluster, clients, observers, gRPC servers, and temp directories. Key helpers include `make_table_key`, `make_record_key`, `make_split_key_at_record`, and `make_encoded_record_key`. Data helpers include `write_records`, `write_records_batched`, `commit_keys`, `just_commit_a_key`, and `just_async_commit_prewrite`. Control helpers include `must_register_task`, `force_flush_files`, `force_flush_files_and_wait`, `run`, `sync`, `wait_with`, `wait_with_router`, `wait_for_flush`, and `must_shuffle_leader`. Verification helpers include `get_files_to_check` and `check_for_write_records`.

## Control Flow
`SuiteBuilder::build` creates a server cluster, installs backup-stream observers into coprocessor hosts, runs the cluster, starts endpoints with local temp paths and backup encryption managers, starts per-store gRPC log-backup services, and waits for metadata watches to initialize. `must_register_task` writes a `StreamTask` with a table range and waits until routers load it. Write helpers generate deterministic TiDB table/record keys, issue prewrite/commit RPCs to region leaders, and return encoded committed MVCC keys. Flush helpers schedule `Task::ForceFlush` and wait on channel completion.

## State And Persistence Behavior
The harness persists metadata into an in-memory slash-etcd-like store and backup files into temp directories. `simple_task` points storage to `flushed_files` and sets zstd compression. `get_files_to_check` parses `v1/backupmeta/*.meta`, extracts file groups and per-CF byte ranges, then `check_for_write_records` reads compressed data segments from data files, decodes stream events, matches write CF keys, follows long-value references into default CF, and rejects missing default entries. `global_checkpoint` queries all endpoints for region checkpoints and returns the minimum.

## Dependencies And Integration Points
The harness binds together backup-stream endpoint/service/resolver/observer/router modules, raftstore `CdcRaftRouter`, region info accessors, resolved-ts leadership resolver, encryption manager, test PD/client/raftstore infrastructure, TiKV transactional RPC clients, protobuf metadata, zstd decoders, and event iterators. It is the main integration boundary for both failpoint and normal backup-stream test modules.

## Risks And Edge Cases
`SuiteBuilder::build` uses a one-second sleep to avoid missing metadata watch updates; that is acknowledged as a harness limitation. `global_checkpoint` is a simplified minimum over endpoint checkpoint reports and does not fully validate region consistency. `check_for_write_records` allows extra keys but reports them, while missing expected keys/default entries fail. The file assumes local Unix sockets/paths and gRPC loopback availability.

## Test Signals
Because this is a harness, its signal comes through the integration tests that consume it. Inline assertions validate every KV prewrite/commit response has no region or key errors, flushes finish within 30 seconds, endpoint sync downcasts to the expected test endpoint type, and decoded backup files contain expected write/default CF records.
