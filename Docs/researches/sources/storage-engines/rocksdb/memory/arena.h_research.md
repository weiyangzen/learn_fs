# sources/storage-engines/rocksdb/memory/arena.h

Purpose: Public declaration for the internal `Arena` allocator.

Important APIs/types/functions: `Arena`, constants `kInlineSize`, `kMinBlockSize`, `kMaxBlockSize`, `kAlignUnit`, `Allocate`, `AllocateAligned`, `ApproximateMemoryUsage`, `MemoryAllocatedBytes`, `AllocatedAndUnused`, `IrregularBlockNum`, `OptimizeBlockSize`, `ScopedArenaPtr`.

Control flow and state: the header documents the two-ended current block strategy: unaligned chunks allocate from one end, aligned chunks from the other. It stores inline memory, regular blocks, huge mappings, current allocation pointers, block accounting, and optional non-owned tracker.

State and persistence behavior: all allocations have arena lifetime. Inline block avoids heap allocation for initial small allocations.

Dependencies and integration points: implements `Allocator` and is used by memtables, skip lists, log buffers, and other short-lifetime internal structures.

Risks: not thread-safe by itself. `ApproximateMemoryUsage` excludes unused current-block space and is an estimate. Objects constructed in arena memory need explicit destruction, supported by `ScopedArenaPtr`.

Test signals: dedicated arena tests cover the major public accounting and allocation contracts.
