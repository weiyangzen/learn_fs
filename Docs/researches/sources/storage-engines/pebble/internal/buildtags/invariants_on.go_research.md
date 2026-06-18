# sources/storage-engines/pebble/internal/buildtags/invariants_on.go

Purpose: Defines build-time `Invariants` as true when the `invariants` tag is present.

APIs and types: Package constant `Invariants = true` behind `//go:build invariants`.

Control flow and state: Compile-time feature flag only.

Persistence and dependencies: No persistence.

Integration points: Enables invariant-heavy code paths and leak detection in cache, locks, and maps.

Risks: Must remain mutually exclusive with `invariants_off.go`; invariant builds may expose latent lifecycle bugs.

Test signals: Covered by invariant-tag CI/test lanes where configured.
