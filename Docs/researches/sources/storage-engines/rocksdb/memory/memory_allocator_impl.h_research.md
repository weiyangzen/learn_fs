# sources/storage-engines/rocksdb/memory/memory_allocator_impl.h

Purpose: Small helper layer for cache/block allocations that may use a configured `MemoryAllocator`.

Important APIs/types/functions: `CacheAllocationDeleter`, `CacheAllocationPtr`, `AllocateBlock`, `AllocateAndCopyBlock`.

Control flow and state: `AllocateBlock` calls allocator `Allocate` when present and returns a `unique_ptr` with a deleter that calls `Deallocate`; otherwise it allocates `new char[size]`. `AllocateAndCopyBlock` allocates the target size and copies `Slice` bytes into the block.

State and persistence behavior: allocation ownership is held by `CacheAllocationPtr`; no persistence.

Dependencies and integration points: block cache/table code needing allocator-aware memory ownership, `Slice`, `MemoryAllocator`.

Risks: deleter stores a raw allocator pointer, so the allocator must outlive returned pointers. `AllocateAndCopyBlock` assumes allocation succeeds and data size is appropriate.

Test signals: indirectly covered by memory allocator block cache test and cache code.
