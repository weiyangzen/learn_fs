# sources/storage-engines/tikv/tests/integrations/server/server.rs

## Purpose
This integration test validates that TiKV's top-level server process can pause and resume its gRPC service via `ServiceEvent` control messages while health checks reflect availability changes.

## Important APIs, Types, and Functions
The main function is `test_restart_grpc_service`. It uses `server::server::run_tikv`, `TikvConfig`, mock PD `test_pd::Server`, `tikv_util::mpsc::unbounded`, `grpcio_health::HealthClient`, and `ServiceEvent::{PauseGrpc, ResumeGrpc, Exit}`. A helper closure retries health checks until `ServingStatus::Serving` appears.

## Control Flow
The test spawns a TiKV server thread with a temp data directory, mock PD endpoint, critical log level, and a selected listen address. The main thread connects a health client, waits for serving status, sends `PauseGrpc`, loops until the health RPC fails with `UNAVAILABLE`, sends `ResumeGrpc`, waits for serving again, then sends `Exit` and joins the server thread.

## State, Persistence, and Dependencies
Persistent state is a temp storage data directory cleaned by test utilities. Runtime state flows through the service-event channel and gRPC health service. The failpoint `mock_force_uninitial_logger` avoids logger initialization conflicts in test context.

## Integration Points, Risks, and Test Signals
This is a process-level integration signal covering server startup, PD binding, health service exposure, control-plane events, and graceful exit. Risks are timeout sensitivity and reliance on local port allocation. The assertions directly check serving, unavailable during pause, and serving after resume.
