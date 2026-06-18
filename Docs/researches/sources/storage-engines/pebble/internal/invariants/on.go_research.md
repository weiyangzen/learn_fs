# sources/storage-engines/pebble/internal/invariants/on.go

## Purpose
`on.go` provides active invariant helper implementations for `invariants` or `race` builds.

## Important APIs, Types, And Functions
`Sometimes(percent)` randomly returns true. `CloseChecker` tracks a `closed` bool and panics on double close, missing close, or use-after-close assertions. `Value[V]` stores and returns an invariant-only value. `MaybeMangle`, `Mangle`, and `BufMangler.MaybeMangleLater` corrupt buffers to detect unsafe retention. `CheckBounds` panics on out-of-range indexes. `SafeSub` panics on underflow. `Integer` mirrors the production constraint.

## Control Flow
Invariant helpers panic through `errors.AssertionFailedf` when violations occur. `BufMangler.MaybeMangleLater` mangles the previously returned cloned buffer on the next call and randomly chooses whether to return a clone or original for the current call.

## State And Persistence Behavior
State is in-memory and exists only in invariant/race builds. Random decisions are process-local via `math/rand/v2`.

## Dependencies And Integration Points
It depends on `math/rand/v2`, `slices`, and `errors`. It is used broadly in iterator wrappers, cache lifecycle checks, arithmetic guards, and bounds checks.

## Risks And Edge Cases
Randomized behavior means invariant failures may be probabilistic; seed capture in higher-level tests is important. `CloseChecker` is not synchronized, so callers using it concurrently need external synchronization. Mangle helpers intentionally destroy buffers and must only be used where this is expected.

## Test Signals
Invariant/race build runs should catch unsafe buffer reuse, double close, arithmetic underflow, and bounds violations that normal builds tolerate or no-op.
