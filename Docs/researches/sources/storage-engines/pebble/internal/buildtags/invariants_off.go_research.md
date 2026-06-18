# sources/storage-engines/pebble/internal/buildtags/invariants_off.go

Purpose: Defines build-time `Invariants` as false when the `invariants` tag is absent.

APIs and types: Package constant `Invariants = false` behind `//go:build !invariants`.

Control flow and state: Compile-time feature flag only.

Persistence and dependencies: No persistence.

Integration points: Invariant checks, leak finalizers, and assertions consult buildtag-driven invariant settings.

Risks: Wrong build constraint would disable or enable expensive/debug checks unexpectedly.

Test signals: Covered by normal builds without the invariants tag.
