# sources/storage-engines/pebble/internal/buildtags/slow_build_on.go

Purpose: Defines build-time `SlowBuild` as true when the `slowbuild` tag is present.

APIs and types: Package constant `SlowBuild = true` behind `//go:build slowbuild`.

Control flow and state: Compile-time feature gate only.

Persistence and dependencies: No persistence.

Integration points: Enables slow or exhaustive paths in selected builds/tests.

Risks: Must remain mutually exclusive with `slow_build_off.go`.

Test signals: Covered by any slowbuild CI lane or manual tag builds.
