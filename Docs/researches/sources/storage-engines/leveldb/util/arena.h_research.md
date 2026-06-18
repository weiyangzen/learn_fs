# sources/storage-engines/leveldb/util/arena.h

## Purpose
`arena.h` declares the arena allocator used by in-memory data structures.

## Important APIs, Types, and Functions
`Arena` exposes `Allocate`, `AllocateAligned`, and `MemoryUsage`. Private helpers allocate fallback/new blocks. Inline `Allocate` handles the fast bump-pointer path.

## Control Flow
Callers allocate nonzero byte spans; memory is freed only when the arena is destroyed. `MemoryUsage` reports allocated block bytes plus pointer-vector accounting through an atomic counter.

## State, Dependencies, and Integration
The arena owns all blocks in `blocks_`. It integrates with memtable internals where individual object deletion is unnecessary.

## Risks and Test Signals
The header notes mixed atomic/non-atomic state access; callers should not concurrently allocate without external synchronization. Tests validate no overwrites and bounded overhead.
