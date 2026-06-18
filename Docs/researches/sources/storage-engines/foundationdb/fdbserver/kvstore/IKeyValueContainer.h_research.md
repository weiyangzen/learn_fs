# sources/storage-engines/foundationdb/fdbserver/kvstore/IKeyValueContainer.h

## Purpose
`IKeyValueContainer.h` defines the default in-memory ordered key-value container used by `KeyValueStoreMemory`. It wraps `IndexedSet<KeyValueMapPair, uint64_t>` with a map-like API and tracks per-node byte weights for memory accounting.

## Important APIs, Types, and Functions
`KeyValueMapPair` owns an `Arena`, `KeyRef`, and `ValueRef`, deep-copying key and value into arena memory. Its comparison operators compare only by key. Free `compare` and `operator<` overloads allow compatible key-like lookups. `IKeyValueContainer` exposes `find`, iteration, `lower_bound`, `upper_bound`, `previous`, `erase`, single and bulk `insert`, `sumTo`, and `getElementBytes`.

## Control Flow
Callers insert by constructing a `KeyValueMapPair`, then passing both the pair and memory weight into `IndexedSet::insert`. Range clears erase iterator spans between lower-bound positions. Range reads are implemented by callers using this ordered API.

## State and Persistence Behavior
All state is process memory in the private `IndexedSet`. It does not persist independently; durability comes from `KeyValueStoreMemory` replaying logged operations into it. `sumTo` provides cumulative byte accounting. `size()` currently returns a placeholder tuple of zeros.

## Dependencies and Integration Points
The direct include is `flow/IndexedSet.h`; the type relies on FoundationDB `Arena`, `KeyRef`, `ValueRef`, and `StringRef` definitions. `KeyValueStoreMemory<IKeyValueContainer>` uses it as the normal memory backend, while the radix-tree backend provides a compatible alternative.

## Risks
The placeholder `size()` may under-report if callers expect real tuple values. Correct memory accounting depends on consistently passing `pair.arena.getSize() + data.getElementBytes()` during inserts. Copy and assignment are private and unimplemented to prevent accidental container copying.

## Test Signals
There are no local tests. Coverage is indirect through memory key-value store tests, range behavior, and tests that compare memory accounting or sequential bulk insert paths.
