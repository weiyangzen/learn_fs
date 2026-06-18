# sources/storage-engines/rocksdb/db/pinned_iterators_manager.h

## Purpose
`pinned_iterators_manager.h` defines `PinnedIteratorsManager`, a `Cleanable` helper that owns iterators or arbitrary pointers pinned during iterator operation and releases them together when pinned data is no longer needed.

## Important APIs, Types, And Functions
The class derives from `Cleanable`. `StartPinning` enables pinning. `PinningEnabled` reports state. `PinIterator` registers an `InternalIterator*` for either normal `delete` or arena-style destructor-only release. `PinPtr` registers any pointer with a release callback. `ReleasePinnedData` releases unique pinned pointers, clears the vector, disables pinning, and calls `Cleanable::Reset`.

Private release helpers are `ReleaseInternalIterator` and `ReleaseArenaInternalIterator`.

## Control Flow
Callers must call `StartPinning` before pinning. Each non-null pointer is appended with its release function. On release or destruction while enabled, the manager sorts the vector of `(ptr, release_func)` pairs, removes duplicate pairs with `std::unique`, invokes each release callback, clears state, and resets inherited cleanups.

## State And Persistence Behavior
The manager stores transient ownership state only. `pinning_enabled` guards lifecycle, and `pinned_ptrs_` stores release work. Move construction/assignment are defaulted, allowing ownership transfer. The destructor releases pinned data if pinning remains enabled.

## Dependencies And Integration Points
The header depends on `table/internal_iterator.h` for `InternalIterator` and `Cleanable`. It integrates with DB/table iterators that need to keep child iterators or resources alive while exposing pinned slices/data to callers.

## Risks
`PinPtr` asserts pinning is enabled, so caller lifecycle ordering matters. Duplicate removal sorts pairs, not just raw pointers; the same pointer registered with different release functions would be released twice, which should never happen.

Arena iterators are destroyed with an explicit destructor call and no deallocation. Passing the wrong `arena` flag would either leak memory or delete arena-owned storage incorrectly. After `ReleasePinnedData`, inherited `Cleanable` cleanup callbacks are also reset, so callers must not expect them to survive.

## Test Signals
Relevant signals are absence of leaks/double frees in iterator tests, pinned resources released on explicit release and destructor paths, and correct behavior when arena-backed internal iterators are pinned.
