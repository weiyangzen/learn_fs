# sources/storage-engines/pebble/internal/buildtags/cgo_off.go

Purpose: Defines build-time `Cgo` as false when the `cgo` build tag is not active.

APIs and types: Package constant `Cgo = false` behind `//go:build !cgo`.

Control flow and state: Compile-time selection only; no runtime control flow.

Persistence and dependencies: No persistence or imports.

Integration points: Manual-memory/cache code uses this constant to choose Go allocation fallbacks when cgo is unavailable.

Risks: Incorrect build constraints would select the wrong allocation strategy.

Test signals: Covered implicitly by building with and without cgo.
