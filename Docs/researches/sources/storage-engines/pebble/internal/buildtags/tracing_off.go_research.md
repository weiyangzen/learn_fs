# sources/storage-engines/pebble/internal/buildtags/tracing_off.go

Purpose: Defines build-time `Tracing` as false when the `tracing` tag is absent.

APIs and types: Package constant `Tracing = false` behind `//go:build !tracing`.

Control flow and state: Compile-time feature flag only.

Persistence and dependencies: No persistence.

Integration points: Reference-count and cache tracing code uses this to compile in lightweight behavior by default.

Risks: Wrong tag constraint would unexpectedly remove or add tracing overhead.

Test signals: Covered by default builds.
