# sources/storage-engines/tikv/components/test_raftstore-v2/Cargo.toml

## Purpose
This manifest defines the private `test_raftstore-v2` crate, a test support crate for TiKV's raftstore-v2 implementation and compatibility with existing raftstore test infrastructure.

## Dependencies And Features
Default features select RocksDB KV engine and raft-engine raft storage by forwarding feature flags to `raftstore`. Additional features enable all-RocksDB and panic-engine modes. Dependencies are extensive and include API versioning, causal timestamps, concurrency management, encryption export, engine traits/Rocks/test engines, filesystem, gRPC health, keys, kvproto, PD client, raft and raftstore crates with `testexport`, `raftstore-v2` with `testexport`, resolved timestamps, resource control/metering, server/service layers, security, temporary files, `test_pd_client`, `test_raftstore`, `test_util`, TiKV, utilities, Tokio, and transaction types.

## State, Persistence, And Integration Points
The manifest describes a high-integration crate that can instantiate real test engines, PD clients, raftstore services, server components, and resource-control paths. Runtime state and persistence are in the source files outside this manifest, but dependency selection here controls whether tests run against RocksDB, raft-engine, or panic engines.

## Risks And Test Signals
Because this crate bridges old and v2 raftstore test infrastructure, dependency/feature drift can create compile-time conflicts or behavior differences. The comment about preferring explicit loggers over `slog-global` signals a known test convenience tradeoff. Successful compilation with the intended features is the first signal; raftstore-v2 integration tests provide behavioral validation.
