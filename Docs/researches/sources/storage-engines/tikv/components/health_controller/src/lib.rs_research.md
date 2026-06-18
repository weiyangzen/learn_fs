# sources/storage-engines/tikv/components/health_controller/src/lib.rs

Purpose: shared `HealthController` facade for TiKV process health, raftstore slow score/trend publication, optional network latency retrieval, and gRPC health-service status.

Important APIs/types/functions: `HealthChecker`, `HealthControllerInner`, `HealthController`, `ServingStatus`, and `RollingRetriever<T>`. Public methods create controllers, set a checker, retrieve slow score/trend, expose gRPC health service, set serving state, read serving status, and shut down.

Control flow: startup initializes gRPC health as `NotServing` and slow score as `1.0`. `set_is_serving` and reporter-only unhealthy-module mutations update `Serving`, `ServiceUnknown`, or `NotServing` while holding the serving-status mutex. `RollingRetriever` writes inactive slots then flips an atomic index.

State and persistence: process-local only. Slow score is an `AtomicU64` containing `f64` bits; slow trend is double-buffered; health checker and serving status are mutex protected.

Dependencies/integration: used by reporters and exposed to TiKV gRPC health. Depends on `grpcio_health`, `kvproto`, `parking_lot`, and collection helpers.

Risks: latency float-to-millis conversion truncates; checker calls happen under mutex; trend reads can be stale by design.

Test signals: unit tests cover serving-state transitions and `RollingRetriever` read/write concurrency.
