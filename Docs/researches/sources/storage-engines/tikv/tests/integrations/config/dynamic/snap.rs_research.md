# sources/storage-engines/tikv/tests/integrations/config/dynamic/snap.rs

## sources/storage-engines/tikv/tests/integrations/config/dynamic/snap.rs

Purpose: verifies dynamic server config updates relevant to snapshot handling.

Important APIs: `ServerConfigManager`, `SnapHandler`, `SnapTask::Validate`, `SnapManager`, `RaftRouterWrap`, `VersionTrack<ServerConfig>`, `ConfigController`, `Module::Server`, and gRPC `ResourceQuota`.

Control flow: `start_server` builds a snap manager, security manager, gRPC environment, raft batch router, lazy snap worker, and server config track. It registers `ServerConfigManager`, starts the snap handler, and returns controller/worker/manager. The test updates `server.snap-io-max-bytes-per-sec` and `server.concurrent-send-snap-limit`, checks the snap manager speed limit, and validates worker config through a scheduled `SnapTask::Validate`.

State and persistence: snapshot state is temporary path backed and runtime config is stored in `VersionTrack`; no durable config file is edited.

Dependencies and integration points: raftstore snap manager, server snap worker, grpcio environment, security manager. Risks include thread scheduling timeouts and the dummy secondary config manager swallowing dispatch. Test signal is exact updated `ServerConfig` plus `SnapManager` byte limit.
