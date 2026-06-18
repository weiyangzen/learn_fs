# sources/storage-engines/rocksdb/memory/arena.cc

Purpose: Implementation of RocksDB’s arena allocator for fast lifetime-based allocation with inline storage, regular blocks, irregular large blocks, and optional huge-page support.

Important APIs/types/functions: `OptimizeBlockSize`, constructor/destructor, `AllocateFallback`, `AllocateFromHugePage`, `AllocateAligned`, `AllocateNewBlock`.

Control flow and state: construction clamps block size, initializes inline block allocation pointers, records inline memory with tracker, and configures huge-page size. Small unaligned allocations use the inline/current block from the high end. Aligned allocations account for alignment slop from the low end. Fallback allocates large requests separately when above one quarter block size; otherwise it allocates a new regular or huge-page block and sets current pointers.

State and persistence behavior: memory lives until arena destruction; no individual frees. `blocks_memory_`, `alloc_bytes_remaining_`, and irregular count expose accounting.

Dependencies and integration points: memtables, log buffers, `MemMapping`, `AllocTracker`, malloc usable size, sync points, logger warnings for huge-page fallback.

Risks: zero-byte allocations are asserted invalid. Huge-page allocation can fail and fall back. Accounting can exceed requested sizes because of allocator usable size and block granularity. Tracker destructor asserts memory was freed/scheduled correctly.

Test signals: `arena_test.cc` validates memory accounting, approximate usage, alignment, lazy mappings, and unmapped large allocation behavior.
