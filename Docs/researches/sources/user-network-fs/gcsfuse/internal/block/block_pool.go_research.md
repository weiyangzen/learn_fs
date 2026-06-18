<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block_pool.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/block_pool.go

Purpose: generic block pool with per-handle limits, reserved blocks, and a global semaphore limiting total mmap-backed memory blocks across readers/writers.

Important APIs/types/functions: `GenBlock`, `GenBlockPool[T]`, `CantAllocateAnyBlockError`, `NewGenBlockPool`, `Get`, `TryGet`, `Release`, `ClearFreeBlockChannel`, `TotalFreeBlocks`, `NewBlockPool`, and `NewPrefetchBlockPool`.

Control flow: construction validates sizes and reserves global semaphore permits. `TryGet` reuses from the free channel or creates a block if limits allow; `Get` loops until reuse/allocation becomes possible. `canAllocateBlock` enforces max blocks and semaphore availability outside reserved slots. Clearing deallocates free blocks and releases permits.

State and persistence: state is in-memory counters, free-block channel, and semaphore permits. Underlying blocks hold mmap memory until deallocated.

Dependencies: `golang.org/x/sync/semaphore`, concrete block factory functions, and callers providing external synchronization; comments explicitly mark the pool as not thread-safe.

Risks: incorrect semaphore release around reserved blocks can leak or over-release global capacity. `Get` can spin/block indefinitely when limits are exhausted and no block is released. Concurrent access without locks can leak memory.

Test signals: `block_pool_test.go` heavily covers config validation, reuse/allocation, blocking behavior, reserved blocks, global limit interactions, and cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block_pool.go -->
