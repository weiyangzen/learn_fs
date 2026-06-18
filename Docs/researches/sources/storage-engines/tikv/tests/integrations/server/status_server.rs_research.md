# sources/storage-engines/tikv/tests/integrations/server/status_server.rs

## Purpose
This test validates the HTTP status server's `/region/{id}` endpoint. It checks that a real cluster region can be fetched from the raft extension and serialized as JSON `RegionMeta`.

## Important APIs, Types, and Functions
`check` builds a Hyper HTTP GET request and validates status, content type, and JSON deserialization. `test_region_meta_endpoint` uses `new_server_cluster`, `StatusServer::new`, `ConfigController::default`, `SecurityConfig::default`, `GrpcServiceManager::dummy`, and the store's `raft_extension`.

## Control Flow
The cluster runs, the test discovers the initial region and peer store, constructs a status server with that store's router, starts it on a free local address, and runs the async `check` future in a Tokio runtime. The server is stopped after validation.

## State, Persistence, and Dependencies
State comes from the live raftstore region metadata and status server listener. Dependencies include Hyper, serde JSON, TiKV status server internals, and raftstore `RegionMeta`.

## Integration Points, Risks, and Test Signals
This exercises the endpoint through HTTP rather than internal calls. Test signals are `200 OK`, `application/json`, and successful `RegionMeta` parsing. It does not assert fields inside `RegionMeta`, so schema validity is covered more than semantic freshness.
