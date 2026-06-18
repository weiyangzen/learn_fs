# sources/storage-engines/pebble/internal/buildtags/cgo_on.go

Purpose: Defines build-time `Cgo` as true when the `cgo` build tag is active.

APIs and types: Package constant `Cgo = true` behind `//go:build cgo`.

Control flow and state: Compile-time selection only.

Persistence and dependencies: No persistence or imports.

Integration points: Cache/manual allocation paths use this to decide whether C-backed manual allocation is available.

Risks: Must stay mutually exclusive with `cgo_off.go`.

Test signals: Covered implicitly by cgo-enabled builds.
