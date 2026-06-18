# sources/storage-engines/tikv/src/server/mod.rs

Purpose: server module root that declares submodules and re-exports the server-facing public API used by the rest of TiKV.

Important APIs/types/functions: exposes config, errors, GC/load/lock manager modules, raft server/KV transports, status/debug services, engine factory types, `GRPC_SERVER_THREAD`, server config constants, proxy helpers, `ConnectionBuilder`, `RaftClient`, `MultiRaftServer`, `RaftKv`, `RaftKv2`, store address resolvers, and server transport.

Control flow: no runtime logic; this is a compile-time module boundary and re-export surface.

State and persistence: none.

Dependencies and integration: coordinates all `crate::server` import paths. Visibility choices here determine which internals are reachable by other crates/modules.

Risks: re-export churn can break downstream imports. Keeping `metrics` crate-visible while re-exporting selected gauges narrows public surface but still permits server internals to share metrics.

Test signals: no direct tests; compilation and downstream module tests validate exports.
