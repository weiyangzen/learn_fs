# sources/storage-engines/pebble/internal/keyspan/bounded.go

## Purpose
`bounded.go` implements `BoundedIter`, a `keyspan.FragmentIterator` wrapper that enforces lower/upper bounds and optionally restricts spans to a prefix-iteration keyspace.

## Important APIs, Types, And Functions
`boundedIterPos` records whether the wrapper is at the lower limit, at the underlying iterator span, or at the upper limit. `BoundedIter` stores the wrapped iterator, current span, comparer, split function, bounds, optional prefix mode pointers, prefix pointer, and position state. Public methods include `Init`, all `FragmentIterator` methods, `SetBounds`, `WrapChildren`, and `TreeStepsNode`. Helpers enforce prefix start/end and forward/backward bounds.

## Control Flow
Seek/first/last operations delegate then filter spans through prefix and directional bounds. `Next` and `Prev` can return nil without advancing the underlying iterator when the current span already overlaps the bound or prefix edge, recording a limit position so a later direction switch can return the saved span. Prefix mode filters spans whose start is after the prefix or end is at/before the prefix.

## State And Persistence Behavior
All state is in-memory wrapper position. `SetBounds` changes dynamic bounds without resetting the underlying iterator directly. `hasPrefix` and `prefix` are pointers so the owner can update prefix mode externally.

## Dependencies And Integration Points
It depends on `base`, `treesteps`, `context`, and `errors`. It wraps keyspan iterators used alongside point iterators, especially when prefix iteration and dynamic bounds need range-key filtering.

## Risks And Edge Cases
The wrapper relies on callers to use `SeekGE` instead of `First` when lower is set and `SeekLT` instead of `Last` when upper is set. Prefix mode disallows most reverse iteration by contract outside an initial seek shape. The saved limit-position logic is subtle but avoids unnecessary underlying movement.

## Test Signals
Coverage is indirect through keyspan and combined iterator tests. Important signals include correct nil-at-bound behavior, direction switches from limit positions, and filtering of spans outside prefix keyspace.
