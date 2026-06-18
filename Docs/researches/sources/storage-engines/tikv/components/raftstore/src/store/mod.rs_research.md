# `sources/storage-engines/tikv/components/raftstore/src/store/mod.rs`

## Purpose
This file is the raftstore store module facade. It declares public and private submodules and re-exports the primary types, functions, routers, worker tasks, metrics, snapshot utilities, unsafe recovery handles, and helper APIs that other TiKV components use.

## Important APIs, Types, and Functions
- Public modules include `cmd_resp`, `config`, `entry_storage`, `fsm`, `local_metrics`, `memory`, `metrics`, `msg`, `region_meta`, `snapshot_backup`, `transport`, `util`, `simple_write`, and `snap`.
- Private modules include async IO, bootstrap, compaction guard, disk probe, fail-fast, hibernate state, peer storage, region snapshot, replication mode, peer/read queue internals, transaction extensions, unsafe recovery, and worker internals.
- Re-exports include bootstrap functions, config, entry storage, `RaftRouter`, `check_sst_for_ingestion`, hibernation types, memory helpers, message/callback types, peer/request helpers, peer storage constants/functions, read queue types, region snapshots, replication state, snapshot managers/utilities, transport traits, transaction extension types, unsafe recovery types/functions, region read progress utilities, and many worker task/controller/stat types.
- `PeerInternalStat` is only re-exported for tests or `testexport`.

## Control Flow
There is no executable control flow beyond module loading and export resolution. The file shapes the public API boundary for `crate::store::*` and controls which internals remain private.

## State and Persistence Behavior
This file owns no state and performs no persistence. Its persistence impact is indirect: it exposes peer storage functions, snapshot managers, bootstrap helpers, and unsafe recovery tools to other modules.

## Dependencies and Integration Points
Every major raftstore subsystem flows through this facade. API consumers can import from `crate::store` instead of deep module paths. The facade is especially important for `fsm/store.rs`, peer modules, server bootstrap, tests, PD workers, transport implementations, and snapshot/unsafe recovery integrations.

## Risks and Edge Cases
- Re-export churn can become a hidden public API break inside the crate.
- Publicly re-exporting too many worker/internal types increases coupling and makes refactors harder.
- Private modules such as `hibernate_state` are still partially exposed through selected re-exports.
- Feature-gated exports must stay aligned with test-only code to avoid build failures under different feature sets.

## Test Signals
There are no local tests. The main signal is whole-crate compilation across normal, test, and `testexport` feature sets. API cleanup should be validated by downstream imports rather than this file alone.
