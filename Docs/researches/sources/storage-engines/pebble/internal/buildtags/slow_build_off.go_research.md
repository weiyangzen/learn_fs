# sources/storage-engines/pebble/internal/buildtags/slow_build_off.go

Purpose: Defines build-time `SlowBuild` as false when the `slowbuild` tag is absent.

APIs and types: Package constant `SlowBuild = false` behind `//go:build !slowbuild`.

Control flow and state: Compile-time feature gate only.

Persistence and dependencies: No persistence.

Integration points: Lets tests or code avoid slow paths unless explicitly requested.

Risks: Build tag name must match the corresponding on file and caller expectations.

Test signals: Covered by default builds.
