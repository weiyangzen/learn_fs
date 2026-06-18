# sources/storage-engines/rocksdb/memory/allocator.h

Purpose: Internal memory allocation interfaces for arena-backed allocations and write-buffer accounting.

Important APIs/types/functions: abstract `Allocator`, `Allocate`, `AllocateAligned`, `BlockSize`, and `AllocTracker` with `Allocate`, `DoneAllocating`, `FreeMem`, `is_freed`.

Control flow and state: `Allocator` defines the allocation contract used by arenas/memtable structures. `AllocTracker` records bytes reserved through a `WriteBufferManager`; implementation in `memtable/alloc_tracker.cc` reserves on allocate, schedules free when allocation phase is done, and frees once.

State and persistence behavior: tracks memory accounting only; no persistence. Allocated memory is freed by allocator lifetime or underlying memory manager.

Dependencies and integration points: `WriteBufferManager`, `Arena`, `ConcurrentArena`, and memtable allocation paths.

Risks: `AllocTracker` is non-copyable and expects precise lifecycle calls. Incorrect `DoneAllocating`/destruction ordering can skew write-buffer pressure accounting.

Test signals: arena tests indirectly exercise allocation; write-buffer manager tests cover tracker implementation outside this subset.
