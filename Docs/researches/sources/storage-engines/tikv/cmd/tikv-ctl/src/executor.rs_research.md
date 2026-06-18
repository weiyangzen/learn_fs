# sources/storage-engines/tikv/cmd/tikv-ctl/src/executor.rs

## Purpose
`executor.rs` abstracts `tikv-ctl` debug operations behind a `DebugExecutor` trait so the CLI can execute the same high-level commands against either a live remote TiKV debug service or local store files opened directly. It is the operational bridge for value dumps, MVCC scans, region and raft inspection, compaction, tombstoning, unsafe recovery, flashback, metrics, and region read-progress diagnostics.

## Important APIs, Types, And Functions
- `new_debug_executor(cfg, data_dir, host, mgr)` chooses remote mode when `host` is present; otherwise it opens local engines under `data_dir`. Local mode detects RaftKV vs RaftKV2 by directory shape, initializes encryption key manager, shared RocksDB env/cache, KV engine factory, raftdb or raft-engine, then returns either `DebuggerImpl<..., ApiV1>` or `DebuggerImplV2`.
- `new_debug_client(host, mgr)` creates a large-message debug gRPC client with TLS/security manager integration.
- `DebugExecutor` is the command surface. Default methods implement user-facing formatting and orchestration; required methods supply backend-specific primitive reads/writes.
- Remote implementation for `DebugClient` maps methods to `debugpb` RPCs such as `get`, `region_info`, `raft_log`, `scan_mvcc`, `compact`, metrics, config mutation, consistency check, flashback, and region read-progress.
- Local implementations for `DebuggerImpl` and `DebuggerImplV2` map the same trait to server debug internals. Several operations remain local-only or remote-only and fail fast when invoked in the wrong mode.
- `handle_engine_error` emits a specific warning for RocksDB LOCK conflicts and exits without encouraging unsafe lock-file removal.

## Control Flow
The main flow is mode selection followed by trait dispatch. Remote mode wraps requests into protobuf messages and exits on RPC errors via `perror_and_exit`. Local mode constructs engines and delegates to `Debugger` methods. Default trait methods validate arguments before calling primitives: MVCC scan checks `z` data-key prefixes and CF names; raw scan checks CF/range/limit; region diff creates a second executor and merges two sorted MVCC streams; compaction translates region metadata to data-key ranges.

Recovery flows are guarded by `check_local_mode`. `set_region_tombstone_after_remove_peer` and `recover_regions_mvcc` fetch authoritative region metadata from PD before local mutation. `recreate_region` fetches a PD region, allocates new region/peer IDs, rewrites epoch and peer metadata, then initializes an empty local region.

## State And Persistence Behavior
Local mode opens persistent KV and raft state directly. It can mutate durable metadata via tombstone, recovery, dropped raft logs, recreated regions, reset-to-version, compaction, and MVCC recovery. Remote mode mutates through TiKV debug RPCs. `get_engine_type` assumes exactly one of `db` or `tablets` exists and asserts otherwise. The file uses `ApiV1` for local `DebuggerImpl` construction, so API-version handling depends on the debug layer and store metadata for other paths.

## Dependencies And Integration Points
This file integrates with `tikv-ctl` command dispatch in `main.rs`, `server::debug`/`debug2`, RocksDB and raft-engine factories, `pd_client::RpcClient`, `security::SecurityManager`, `kvproto::debugpb`, raft protobuf decoding, `raftstore` key-range helpers, encryption config, and engine traits. It also shares formatting and exit helpers from `util.rs`.

## Risks And Edge Cases
- Local direct-engine access is dangerous if TiKV is still running; `handle_engine_error` detects LOCK conflict but other concurrent-access hazards still rely on RocksDB/engine behavior and operator discipline.
- `get_engine_type` unwraps directory reads and asserts mutually exclusive layout; unusual or partially migrated data directories will panic.
- Remote/local parity is incomplete. Raw scan is remote-unimplemented, metrics and consistency/config mutation are local-unavailable, and several V2 recovery methods are unimplemented.
- MVCC scan and diff can be expensive over large ranges; `limit == 0` means unbounded range scan in several paths.
- Flashback retry handling is implemented in `main.rs`; this file’s remote `flashback_to_version` only returns a retry tuple with the failed range and error.

## Test Signals
There are no unit tests in this file. Coverage is indirect through `tikv-ctl` command tests, server debug tests, backup/flashback integration tests, and compile-time trait conformance for `DebugClient`, `DebuggerImpl`, and `DebuggerImplV2`. The explicit warnings and mode guards are important manual-test targets.
