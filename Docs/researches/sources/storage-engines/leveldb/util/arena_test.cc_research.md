# sources/storage-engines/leveldb/util/arena_test.cc

## Purpose
`arena_test.cc` stress-tests arena allocation behavior.

## Important APIs, Types, and Functions
Tests `ArenaTest.Empty` and `ArenaTest.Simple` instantiate `Arena`, randomly allocate normal and aligned buffers, fill each allocation, and verify contents later.

## Control Flow
The simple test performs 100,000 allocations with skewed sizes, including large allocations, tracks total requested bytes, checks `MemoryUsage` is at least requested and eventually within 10% overhead, then validates each byte pattern.

## State, Dependencies, and Integration
It depends on `util/random` and gtest. It specifically covers allocation lifetime across later allocations.

## Risks and Test Signals
The test catches overlap, alignment path corruption, and excessive overhead for steady-state small allocations. It does not cover concurrent allocation.
