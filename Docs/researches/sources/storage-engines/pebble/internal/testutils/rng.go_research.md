# sources/storage-engines/pebble/internal/testutils/rng.go

## Purpose
This file provides small random data helpers for tests.

## Important APIs, Types, and Functions
`RandIntInRange(r,min,max)` returns an integer in `[min,max)`. `RandBytes(r,size)` returns a byte slice of the requested length filled with random ASCII letters from `a-zA-Z`, or nil for non-positive sizes.

## Control Flow and State
`RandIntInRange` delegates to `r.IntN(max-min)`. `RandBytes` allocates a slice, fills each byte by sampling from `randLetters`, and returns it. `randLetters` is package-level constant data.

## Dependencies and Integration
It depends on `math/rand/v2`. These helpers are useful for randomized tests that need deterministic behavior through caller-supplied RNGs.

## Risks and Edge Cases
`RandIntInRange` panics if `max <= min` because `IntN` receives a non-positive argument. `RandBytes` returns nil rather than an empty non-nil slice for `size <= 0`, which callers should account for.

## Test Signals
No direct tests are included. Behavior is simple and likely covered by randomized test consumers.
