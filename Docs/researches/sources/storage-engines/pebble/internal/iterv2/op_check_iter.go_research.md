# sources/storage-engines/pebble/internal/iterv2/op_check_iter.go

## Purpose
`op_check_iter.go` wraps an `iterv2.Iter` and enforces legal operation sequences, especially around direction, exhaustion, bounds, prefix mode, boundary keys, and `TrySeekUsingNext`.

## Important APIs, Types, And Functions
`iterState` tracks unpositioned, forward/backward valid/exhausted, and prefix valid/exhausted states. `IllegalOpError` marks expected illegal operations during random generation. `OpCheckIter` stores inner iterator, comparer, state, boundary flag, last key, bounds, last seek mode, try-seek boundary, and optional prefix-change enforcement. Public APIs include `NewOpCheckIter` and `RequirePrefixChangeForTrySeekUsingNext`; all `Iter` methods are implemented.

## Control Flow
Before delegating, each method validates its preconditions. Seek methods validate bounds and `TrySeekUsingNext` constraints, then set new seek state. `Next`, `Prev`, and `NextPrefix` reject invalid states and update try-seek boundaries. Transition helpers update `lastKey`, `atBoundary`, and state based on returned KV. `SetBounds` resets position state.

## State And Persistence Behavior
The wrapper maintains only operation-state metadata. It does not persist data. On illegal operations it panics before altering the wrapped iterator, which lets random tests skip illegal operations safely.

## Dependencies And Integration Points
It depends on `base`, `treesteps`, `context`, `bytes`, and formatting. `CheckIter` uses it around the reference iterator to determine whether a randomly chosen operation is legal.

## Risks And Edge Cases
The legality rules mirror the long contract in `iter.go`; mistakes here can make tests skip valid operations or allow invalid ones. The special `RequirePrefixChangeForTrySeekUsingNext` mode is not general iterv2 behavior and is only for a merging-iterator-specific test mode.

## Test Signals
Random tests rely on `IllegalOpError` classification. Failures often include operation logs showing which legality rule diverged from implementation behavior.
