# sources/storage-engines/tikv/components/test_pd/src/server.rs

## Purpose
This file implements the gRPC mock PD server. It hosts PD, MetaStorage, and resource-manager services, dispatches calls to optional case-specific mockers, falls back to the default `Service`, and exposes helpers for tests to start/stop servers and build clients.

## Important APIs, Types, And Functions
`Server<C>` owns an optional grpcio server and a `PdMock<C>`. `Server<Service>::new` creates a default service-backed server. `Server::with_case` injects an `Arc<C: PdMocker>`. `with_configuration` builds the default handler, mock wrapper, TSO logical counter, and in-memory etcd client, then starts the server. `start` registers PD, MetaStorage, and resource-manager services, binds through `SecurityManager`, injects bound endpoints into handlers, and sleeps briefly for readiness. `bind_addrs` exposes actual bound addresses.

`hijack_unary` is the central dispatch helper for unary RPCs. It tries the case mocker, then default handler, maps `Ok` to successful sink responses, `Err` to gRPC UNKNOWN failures, and `None` to UNIMPLEMENTED unless the `connect_leader` failpoint rewrites it as UNAVAILABLE.

`PdMock<C>` implements `MetaStorage`, `Pd`, and `resource_manager::ResourceManager`. It implements streaming TSO, region heartbeat, bucket reporting, token bucket acquisition, and many unary PD RPCs through `hijack_unary`.

## Control Flow And State
The mock is cloneable via shared `Arc`s. TSO streaming uses an atomic logical counter with fixed physical time `42`. Region heartbeat and resource-manager streams filter incoming requests through case/default mockers and send responses only when mockers return `Some(Ok(_))`. MetaStorage watch delegates directly to the case mocker and otherwise returns unimplemented.

## Persistence And Integration Points
All server state is in-memory: default service state, optional case state, TSO counter, and etcd client. It integrates tightly with grpcio generated service traits, `security::SecurityManager`, PD client error conversion, failpoints, and protobuf service definitions.

## Risks And Test Signals
`stop` panics if the server is not started. The one-second startup sleep is coarse and can slow tests. Several PD RPCs remain `unimplemented!()`, so tests must avoid unsupported methods or extend the mock. Streaming sinks often ignore or unwrap send results, which is acceptable for controlled tests but can panic on unexpected disconnects. Correct dispatch ordering is the key behavior to validate when adding mockers.
