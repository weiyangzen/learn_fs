# sources/storage-engines/pebble/internal/keyspan/assert_iter_test.go

## Purpose
`assert_iter_test.go` datadriven-tests bound checking for `keyspan.AssertBounds` and `AssertUserKeyBounds`.

## Important APIs, Types, And Functions
`TestAssertBoundsIter` supports `define`, `assert-bounds`, and `assert-userkey-bounds`. It parses spans with `ParseSpan`, constructs a `NewIter`, wraps it, iterates forward, and captures panics as output.

## Control Flow
`define` replaces the span fixture. Assertion commands read a two-line lower/upper input, choose internal-key or user-key lower bound mode, iterate from `First` through `Next`, and return `OK` or the panic message.

## State And Persistence Behavior
The span fixture persists across datadriven commands in the test closure. Golden behavior lives in `testdata/assert_iter`.

## Dependencies And Integration Points
It depends on `datadriven`, `base`, `testkeys`, `testify/require`, and keyspan iterator helpers.

## Risks And Edge Cases
The test only iterates forward from first; it focuses on bounds rather than `SeekGE`, `SeekLT`, or reverse ordering assertions. Panic messages include the wrapped type, so type-name changes can affect goldens.

## Test Signals
Golden output confirms lower user-key, lower internal-key trailer, and upper-bound violations are detected while valid spans pass.
