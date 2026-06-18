# sources/storage-engines/foundationdb/flow/include/flow/Deque.h

## Purpose
`Deque.h` implements a small STL-like double-ended queue backed by a circular power-of-two array. It is used where Flow wants predictable allocation and vector-like invalidation semantics.

## Important APIs, Types, And Functions
The template `Deque<T>` provides copy/move construction, assignment, `push_back()`, `emplace_back()`, `pop_back()`, `pop_front()`, `clear()`, `size()`, `empty()`, `capacity()`, `front()`, `back()`, `operator[]`, and bounds-checked `at()`.

## Control Flow
Insertions grow when full, constructing elements in-place at `end & mask`. `grow()` doubles capacity, moves existing elements into a new aligned array starting at zero, destroys old elements, frees old storage, and resets indices. `pop_front()` advances or unwraps indices when `begin` reaches `mask`.

## State And Persistence Behavior
State is `arr`, `begin`, `end`, and `mask`; capacity is `mask + 1`. Elements live only in constructed slots. No persistence exists beyond object lifetime. Reallocation invalidates references and iterators.

## Dependencies And Integration Points
It depends on `flow/Platform.h` for aligned allocation/free and `platform::outOfMemory`, plus Flow `ASSERT`. It is used by other Flow internals such as `IndexedSet` async free prefetch queues.

## Risks And Edge Cases
`T` must be nothrow destructible for grow cleanup. Capacity is capped by `max_size()`. Copy paths must handle wrapped source ranges. `front()` and `back()` assume non-empty. Manual allocation/destruction makes exception safety in `grow()` the key risk.

## Test Signals
Tests should cover wrapping, growth, copy and move assignment, equality, exception during move/copy construction, bounds checking, destructor counts, and use with over-aligned element types.
