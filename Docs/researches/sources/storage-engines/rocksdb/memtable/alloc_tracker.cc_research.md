# sources/storage-engines/rocksdb/memtable/alloc_tracker.cc

## Purpose
`alloc_tracker.cc` implements `AllocTracker`, a small accounting adapter between allocator users and `WriteBufferManager`. It records bytes allocated by an arena-backed owner, reserves those bytes in the write-buffer manager, and later transitions them from active mutable memory to scheduled-for-free and finally freed memory.

## Important APIs and Functions
- `AllocTracker::AllocTracker(WriteBufferManager*)` stores the optional manager and initializes `bytes_allocated_`, `done_allocating_`, and `freed_`.
- `Allocate(size_t bytes)` is called when memory is allocated. If the manager is enabled or charging cache, it increments `bytes_allocated_` with relaxed atomics and calls `WriteBufferManager::ReserveMem`.
- `DoneAllocating()` marks the allocation owner as no longer mutable. It calls `ScheduleFreeMem(total_bytes)` exactly once, which reduces `memory_active_` in the manager while keeping total usage reserved.
- `FreeMem()` first ensures `DoneAllocating()` has happened, then calls `WriteBufferManager::FreeMem(total_bytes)` once. The destructor delegates to this method.

## Control Flow and State
The class is a lifecycle tracker. `Allocate()` may be called many times while a memtable/arena is active. `DoneAllocating()` is a one-way transition guarded by `done_allocating_`. `FreeMem()` is another one-way transition guarded by `freed_`, and it tolerates callers that forgot to call `DoneAllocating()`. `bytes_allocated_` is atomic, but the transition booleans are plain fields, so the lifecycle itself is expected to be externally serialized or owned by a single object.

## Dependencies and Integration Points
The implementation depends on `rocksdb/write_buffer_manager.h`, `memory/allocator.h`, and `memory/arena.h`. It is used by allocation-owning RocksDB components to keep global write-buffer pressure synchronized with arena memory. It directly drives `ReserveMem`, `ScheduleFreeMem`, and `FreeMem`, so its correctness affects flush pressure, stall decisions, and optional cache reservation charging.

## Risks and Test Signals
The main risk is lifecycle imbalance: missing `FreeMem()` would leak write-buffer accounting, while double free is prevented by `freed_`. If `WriteBufferManager` is disabled and not charging cache, the tracker asserts no bytes were recorded. The paired behavior is indirectly tested by write-buffer-manager tests that verify active/total memory transitions; there is no dedicated test in this file.
