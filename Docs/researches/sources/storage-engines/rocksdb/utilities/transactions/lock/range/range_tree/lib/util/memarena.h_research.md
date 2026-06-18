# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/memarena.h

## Purpose
Declares the `memarena` arena allocator and its chunk iterator.

## Important APIs, Types, And Functions
Public methods are `create`, `destroy`, `malloc_from_arena`, `move_memory`, `total_memory_size`, `total_size_in_use`, `total_footprint`, and nested `chunk_iterator::{current,next,more}`. Internal `arena_chunk` stores `buf`, `used`, and `size`.

## Control Flow
The header defines construction defaults and the iterator's conceptual order: `_current_chunk` is represented by index `-1`, followed by `_other_chunks`.

## State And Persistence Behavior
The object owns all chunk memory until destroyed or moved. State is in memory only.

## Dependencies And Integration Points
Included by locktree utility code needing stable addresses and bulk-free behavior. `standalone_port.cc` provides the memory footprint helper used by the implementation.

## Risks And Edge Cases
Manual `create`/`destroy` lifetime is required despite a C++ constructor. The iterator exposes raw memory plus used byte counts and depends on the arena remaining alive and unchanged. It is not thread-safe.

## Test Signals
Header contract is validated by implementation tests and by any locktree path that copies or iterates arena chunks.
