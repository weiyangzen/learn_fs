# sources/storage-engines/tikv/tests/benches/misc/raftkv/mod.rs

## Purpose
This module benchmarks `RaftKv` async snapshot and async write wrapper overhead using a synchronous fake raftstore router.

## Important APIs, Types, and Functions
`SyncBenchRouter` stores a `RocksEngine` and `Region`, implements raftstore router traits, and directly invokes read/write callbacks. `new_engine` creates a temporary RocksDB engine with all CFs. Benchmarks include `bench_async_snapshots_noop`, `bench_async_snapshot`, and `bench_async_write`.

## Control Flow
The router's `invoke` builds a `RaftCmdResponse`, returns a `RegionSnapshot` for read callbacks, or returns a write response with the request command type. `bench_async_snapshots_noop` measures nested callback conversion without `RaftKv`. `bench_async_snapshot` constructs a region/context and calls `RaftKv::async_snapshot`. `bench_async_write` calls `tikv_kv::write` with a delete modify.

## State and Persistence Behavior
Temporary RocksDB engines are created under temp dirs. The fake router avoids real raft persistence/replication; writes are measured as wrapper/future construction through `RaftKv` and callback path rather than real raftstore execution.

## Dependencies and Integration Points
It depends on engine_rocks, engine_traits CF constants, raftstore router traits, `RaftKv`, region snapshot types, `tikv_kv::write`, and transaction key types.

## Risks and Test Signals
Because the router is synchronous and fake, results are lower-bound overhead signals rather than full raftstore performance. Trait implementation drift will show up as compilation failures.
