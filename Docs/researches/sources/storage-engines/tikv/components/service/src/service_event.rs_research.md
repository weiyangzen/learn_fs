# sources/storage-engines/tikv/components/service/src/service_event.rs

Purpose: defines the service-control messages sent from signal/control code to the server event loop.

Important APIs and types: `ServiceEvent` variants are `PauseGrpc`, `ResumeGrpc`, `GracefulShutdown`, and `Exit`. A manual `Debug` implementation emits stable tuple-style variant names.

Control flow and integration: `server2.rs` receives these events and calls `pause`, `resume`, `graceful_shutdown`, or breaks the main loop. `signal_handler.rs` sends `GracefulShutdown` or `Exit` on process signals. `GrpcServiceManager` sends pause/resume variants.

State and persistence behavior: no local state or persistence; this is an in-memory channel protocol.

Risks: enum changes must update all match sites in server and service manager. `Debug` is manual, so new variants require manual formatting.

Test signals: no direct tests.
