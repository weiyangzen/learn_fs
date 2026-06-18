# sources/storage-engines/tikv/src/server/server.rs

Purpose: manages TiKV's gRPC server, raft transport, snapshot worker, health service, stats tasks, memory quota, and dynamic service registration.

Important APIs/types/functions: `GrpcBuilderFactory`; `BuilderFactory`; `Server<S, E>`; `new`; `build_and_bind`; `start`; `stop`; `pause`; `resume`; `register_service`; `transport`.

Control flow: `Server::new` creates optional stats runtime, thread-load tracking, lazy snapshot worker, raft extension, `KvService`, memory quota, secure gRPC builder, connection builder, `RaftClient`, health checker, and `ServerTransport`. `build_and_bind` transforms builder into bound server and records actual address. `start` launches legacy/tablet snapshot runner, starts gRPC, starts periodic load and memory gauges, records startup version/build metrics, and marks health serving. Pause/resume rebuild and rebind gRPC around health state.

State/persistence: runtime-only state: `builder_or_server`, local address, transport, snap worker, stats/read/debug pools, health controller, memory quota. No direct storage persistence.

Dependencies/integration: `KvService`, security manager, health controller, raft client/transport, resolver, snap managers, coprocessor endpoints, GC worker, resource group manager, global timer, and metrics. Risks include unwrap-heavy lifecycle shape assumptions, registration only before server build/start, pause/resume bind failure paths, and background stats task shutdown. Test `test_peer_resolve` covers unresolved/resolved raft message behavior and unreachable reporting.
