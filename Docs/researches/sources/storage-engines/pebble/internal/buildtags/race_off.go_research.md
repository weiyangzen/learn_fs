# sources/storage-engines/pebble/internal/buildtags/race_off.go

Purpose: Defines build-time `Race` as false when the race detector tag is absent.

APIs and types: Package constant `Race = false` behind `//go:build !race`.

Control flow and state: Compile-time selection only.

Persistence and dependencies: No persistence.

Integration points: Used by invariant/finalizer/manual-memory code to avoid incompatible behavior under race builds.

Risks: Incorrect constraint would misclassify race builds.

Test signals: Covered by non-race builds.
