# sources/storage-engines/pebble/internal/invariants/off.go

## Purpose
`off.go` provides no-op implementations of invariant helpers for normal builds without `invariants` or `race` tags.

## Important APIs, Types, And Functions
`Sometimes` always returns false. `CloseChecker` has no-op `Close`, `AssertClosed`, and `AssertNotClosed`. Generic `Value[V]` stores nothing; `MakeValue`, `Get`, and `Set` no-op or return zero values. `MaybeMangle`, `Mangle`, and `BufMangler.MaybeMangleLater` do nothing. `CheckBounds` no-ops. `SafeSub` returns zero on underflow instead of panicking. `Integer` defines supported integer constraints.

## Control Flow
All functions are constant or no-op. This allows invariant calls to remain in production code with near-zero behavior.

## State And Persistence Behavior
No invariant state is stored in normal builds. Zero-sized structs can still influence parent struct layout when placed last, as comments note.

## Dependencies And Integration Points
The file has build tag `!invariants && !race`. It imports `errors` only blankly to keep API symmetry or dependency expectations.

## Risks And Edge Cases
`SafeSub` silently clamps underflow to zero in production, so callers must not rely on panic behavior outside invariant builds. Zero-sized fields can affect addressability/layout in subtle ways.

## Test Signals
Normal-build tests should show no invariant panics and should verify code remains correct when invariant helpers do not enforce checks.
