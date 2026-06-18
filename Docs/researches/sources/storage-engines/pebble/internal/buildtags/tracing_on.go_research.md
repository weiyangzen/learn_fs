# sources/storage-engines/pebble/internal/buildtags/tracing_on.go

Purpose: Defines build-time `Tracing` as true when the `tracing` tag is present.

APIs and types: Package constant `Tracing = true` behind `//go:build tracing`.

Control flow and state: Compile-time flag only.

Persistence and dependencies: No persistence.

Integration points: Enables reference-count/cache tracing paths that help diagnose leaks and lifecycle bugs.

Risks: Tracing may significantly slow execution; constraints must match off file.

Test signals: Covered by tracing-tag diagnostic builds if run.
