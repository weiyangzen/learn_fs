# sources/storage-engines/pebble/internal/buildtags/race_on.go

Purpose: Defines build-time `Race` as true when built with the race detector.

APIs and types: Package constant `Race = true` behind `//go:build race`.

Control flow and state: Compile-time flag only.

Persistence and dependencies: No persistence.

Integration points: Allows code to disable finalizers or unsafe/manual-memory features that interfere with race detection.

Risks: Must stay paired with `race_off.go`.

Test signals: Covered by race-enabled CI/test runs.
