# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/cluster.rs

## Purpose
This file is the shared raftstore-v2 integration-test harness. It builds in-process test clusters with real raftstore-v2 batch systems, raft engines, tablet registries, PD clients, snapshot managers, coprocessor hosts, importers, resource controllers, and a channel-backed transport. It also provides high-level helpers for writing, querying, splitting, merging, dispatching raft messages, and asserting peer life-cycle state.

## Important APIs, Types, and Functions
- `check_skip_wal()` asserts RocksDB WAL files exist but are empty, validating WAL-skipping behavior.
- `TestRouter` wraps `RaftRouter<KvTestEngine, RaftTestEngine>` and adds `query`, `simple_write`, `admin_command`, `wait_flush`, `wait_applied_to_current_term`, `new_request_for`, `stale_snapshot`, `region_detail`, and `refresh_bucket`.
- `RunningState` owns live store components and shuts down the system/background worker on drop.
- `TestNode` owns PD client, temp path, optional running state, logger, and resource manager; it can start, stop, restart, expose registry/PD client/state/id.
- `TestTransport` implements raftstore-v2 `Transport` with a channel and flush counter.
- `v2_default_config()` sets test defaults, while `disable_all_auto_ticks()` disables automatic ticks so tests can drive behavior manually.
- `Cluster` owns nodes, routers, receivers, and PD server; it supports single/multi-node construction, restart, node/receiver access, and `dispatch()` to route all pending raft messages including snapshot file handoff.
- `split_helper`, `merge_helper`, and `life_helper` provide reusable admin-command and assertion utilities.

## Control Flow
`RunningState::new()` creates encrypted temp raft engine, bootstraps store and first region, creates the batch system, configures state storage, creates a tablet factory/registry and initial tablet, wraps the router, builds snapshot manager/coprocessor host/importer/background workers, and starts the raftstore-v2 system. `Cluster::with_configs()` disables ticks, creates each `TestNode`, starts it with a channel transport, and records routers/receivers. `Cluster::dispatch()` drains queued raft messages, finds target nodes by store id, simulates snapshot transfer by moving snapshot directories and encryption metadata, sends messages to routers, waits for flushes, and repeats until no messages remain.

## State and Persistence Behavior
The harness uses real temp directories for raft engines, tablet directories, tablet snapshots, and SST importer data. Restart drops `RunningState` and recreates it against the same temp path and PD client, preserving raft/tablet state. Snapshot transfer physically renames generated snapshot directories into receive paths and migrates encryption metadata. `stale_snapshot()` issues a stale-read snapshot request using write-batch flags.

## Dependencies and Integration Points
The file integrates `engine_test`, `engine_traits`, `raftstore_v2::{Bootstrap, StateStorage, StoreSystem, create_store_batch_system}`, raftstore store/coprocessor types, `test_pd`, `SstImporter`, encryption data-key management, resource control, concurrency manager, and TiKV worker utilities. It is imported by both normal integration and failpoint test targets.

## Risks and Edge Cases
- Automatic ticks are disabled, so tests must explicitly send ticks/dispatch messages; forgetting this can look like a product bug.
- `dispatch()` simulates snapshot transfer by filesystem rename and key import, so it must stay aligned with real snapshot manager paths.
- `wait_applied_to_current_term()` assumes commit/applied index and commit term are enough to prove current-term apply.
- Restart preserves temp path state but rebuilds runtime resources; tests relying on in-memory only state must account for loss.
- The shared path import into failpoint tests means helper behavior changes have broad blast radius.

## Test Signals
All integration/failpoint tests in this subset rely on this harness. It emits strong signals through debug info, stale snapshots, PD client reads, raft-engine direct reads, transport receiver messages, and tablet filesystem checks.
