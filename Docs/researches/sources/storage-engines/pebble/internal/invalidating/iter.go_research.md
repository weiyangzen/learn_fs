# sources/storage-engines/pebble/internal/invalidating/iter.go

## Purpose
`invalidating/iter.go` wraps `base.InternalIterator` implementations to catch callers that incorrectly retain returned key/value buffers after subsequent iterator movement.

## Important APIs, Types, And Functions
`MaybeWrapIfInvariants` randomly wraps iterators in invariant builds. `Option` and `IgnoreKinds` configure key kinds whose buffers should not be trashed. `NewIter` returns a `base.TopLevelIterator` wrapper. The private `iter` implements the internal iterator methods, copying returned `InternalKV`s in `update` and trashing the previous copy in `trashLastKV`.

## Control Flow
Every positioning method delegates to the wrapped iterator and passes the result to `update`. `update` trashes the prior copy, clones key and lazy value/fetcher state for the new result, and returns the copy. On nil results, it clears `lastKV`. Non-positioning methods mostly delegate.

## State And Persistence Behavior
Wrapper state is in-memory: the underlying iterator, last copied KV, ignored key-kind mask, and an unused local `err` field. The wrapper intentionally mutates prior returned copies to expose unsafe retention bugs.

## Dependencies And Integration Points
It depends on `base`, `invariants`, `treesteps`, `context`, and `slices`. It is used in tests and invariant builds around point iterators, including iterv2 random tests.

## Risks And Edge Cases
`SeekPrefixGEStrict` delegates to `SeekPrefixGE`, matching the underlying interface but not adding different behavior. Ignored key kinds can hide reuse issues for those kinds by design. The wrapper copies visible lazy fetcher fields by assignment and then zeroes on trash.

## Test Signals
Coverage is indirect through invariant/random iterator tests. Bugs surface as corrupted retained keys/values when callers retain slices across operations.
