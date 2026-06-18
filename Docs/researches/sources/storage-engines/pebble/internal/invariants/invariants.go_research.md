# sources/storage-engines/pebble/internal/invariants/invariants.go

## Purpose
`invariants.go` centralizes build-tag-controlled invariant flags and finalizer handling for Pebble.

## Important APIs, Types, And Functions
`Enabled` is true for `race` or `invariants` builds. `RaceEnabled` mirrors the race build tag. `UseFinalizers` is true for invariant or tracing builds except race. `SetFinalizer(obj, finalizer)` wraps `runtime.SetFinalizer` and no-ops when `UseFinalizers` is false.

## Control Flow
All values are compile-time constants from `internal/buildtags`. `SetFinalizer` checks `UseFinalizers` at runtime and delegates to `runtime.SetFinalizer` only when enabled.

## State And Persistence Behavior
No persistent state is stored. The effect is compile-time/runtime gating of expensive assertions and finalizer-based lifecycle checks.

## Dependencies And Integration Points
It depends on `runtime` and `buildtags`. Other packages use `invariants.Enabled`, `Sometimes`, `CloseChecker`, `Value`, `SafeSub`, and finalizer helpers from this package.

## Risks And Edge Cases
Comments warn not to substantially change production paths solely under `Enabled`; randomized `Sometimes` wrapping is preferred so production paths still receive coverage. Finalizers are deliberately disabled under race due to historical detector issues.

## Test Signals
Signals are build-tag matrix tests: normal builds should compile away invariant-only behavior, while race/invariant builds should activate checks without finalizer races.
