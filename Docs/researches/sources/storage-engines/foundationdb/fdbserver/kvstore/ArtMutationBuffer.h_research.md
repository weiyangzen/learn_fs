# sources/storage-engines/foundationdb/fdbserver/kvstore/ArtMutationBuffer.h

## Purpose
Defines `MutationBufferART`, an arena-backed adaptive radix tree wrapper for range mutation boundaries.

## Important APIs, Types, and Functions
- Private `Arena arena` and `art_tree* mutations` own tree nodes and `RangeMutation` values.
- `const_iterator` and `iterator` wrap `art_iterator` and expose key/mutation access, comparison, increment/decrement, and mutable value pointer access.
- Constructor creates sentinel boundaries at `dbBegin.key` and `dbEnd.key`; `dbEnd` is marked as a clear boundary.
- `copyToArena<T>` deep-copies compatible objects into the arena.
- `upper_bound`, `lower_bound`, `erase(begin,end)`, and `insert(KeyRef)` provide ordered access and boundary mutation.

## Control Flow
Construction seeds full-keyspace sentinels. `insert` uses `insert_if_absent`; existing boundaries are returned unchanged. New boundaries allocate a `RangeMutation`, inspect the previous boundary, and inherit clear-all state when the previous boundary clears after itself. `erase` walks and removes a half-open iterator range while preserving the next iterator before each deletion.

## State and Persistence Behavior
All state lives in the arena and ART until buffer destruction. There is no persistence or per-node freeing.

## Dependencies and Integration Points
Depends on `art.h`, `flow/Arena.h`, `KeyRef`, `dbBegin`, `dbEnd`, and `RangeMutation`. It is a lower-level KV storage mutation-buffer utility.

## Risks and Edge Cases
Iterator erase relies on ART iterator validity rules. Values are stored as `void*` and cast to `RangeMutation`. Boundary clear propagation is semantically important for range mutation correctness. Arena lifetime can retain unused allocations.

## Test Signals
No direct tests in this subset; expected coverage comes through KV-store mutation and range-clear tests.
