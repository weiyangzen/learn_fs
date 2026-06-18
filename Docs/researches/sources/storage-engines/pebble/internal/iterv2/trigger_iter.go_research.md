# sources/storage-engines/pebble/internal/iterv2/trigger_iter.go

## Purpose
`trigger_iter.go` implements an `iterv2.Iter` that emits a synthetic boundary before iteration touches a region with nonzero count, then fires a callback and permanently exhausts itself.

## Important APIs, Types, And Functions
`BoundaryTrigger` defines `Trigger(key, dir)`. `TriggerIter` stores a comparer, `regiontree.T[[]byte,int]`, trigger callback, bounds, no-region flag, direction, current boundary KV, and span. Public methods include `Init`, `Reset`, all `Iter` methods, and tree/string helpers. Helpers include `checkNoRegions`, `makeBoundaryKey`, `upperBound`, `lowerBound`, `exhaust`, `fire`, `seekForward`, and `seekBackward`.

## Control Flow
Initialization checks whether any positive-count region intersects bounds. Forward seeks enumerate regions from a lower bound; if the seek key is inside a region, the trigger fires immediately, otherwise the iterator returns a boundary at the next region start. Backward seeks mirror this using region ends. `Next`/`Prev` fire when advancing past a presented boundary; direction switches reseek from the current boundary. `Reset` installs a new trigger and re-evaluates region availability.

## State And Persistence Behavior
State is in-memory and one-shot: after `fire`, `trigger` becomes nil, `noRegions` is true, and the iterator exhausts. Bounds can be changed with `SetBounds`.

## Dependencies And Integration Points
It depends on `axisds/regiontree`, `base`, `invariants`, `treesteps`, and `errors`. It supports lazy combined iteration where reaching a region triggers loading or activation of range-key state.

## Risks And Edge Cases
Seek keys exactly inside regions fire immediately instead of returning a boundary. `TrySeekUsingNext` has a randomized invariant fast path that can expose misuse. Nil trigger disables the iterator. Correct regiontree sentinel bounds are essential for nil lower/upper.

## Test Signals
`trigger_iter_test.go` covers region definition, forward/backward iteration, bounds, continuation after a boundary, and emitted trigger events.
