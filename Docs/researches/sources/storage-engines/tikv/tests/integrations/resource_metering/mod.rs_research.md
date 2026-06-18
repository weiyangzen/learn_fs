# sources/storage-engines/tikv/tests/integrations/resource_metering/mod.rs

Purpose: module wiring for resource metering integration tests.

Important APIs and functions: exports `test_read_keys` and `test_suite` unconditionally; conditionally exports `test_dynamic_config`, `test_receiver`, `test_pubsub`, and `test_cpu` on Linux/macOS via `#[cfg(any(target_os = "linux", target_os = "macos"))]`.

Control flow: no runtime logic; Rust module inclusion determines which test files compile for the target OS.

State and persistence: none directly. Included modules create temporary storage, workers, and mock gRPC services when their tests run.

Dependencies and integration: links the resource metering test subtree into the integration test harness and gates platform-dependent accounting tests.

Risks: changing cfg gates can either hide supported coverage or compile unstable platform-specific tests elsewhere.

Test signals: successful compilation and expected test discovery are the direct signals.
