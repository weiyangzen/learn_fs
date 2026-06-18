# sources/storage-engines/foundationdb/flow/include/flow/FastAlloc.h

## Purpose
`FastAlloc.h` declares Flow's fixed-size fast allocator, allocation instrumentation, keepalive allocator testing hooks, and allocation helpers used by hot actor/container objects.

## Important APIs, Types, And Functions
Key APIs are `FastAllocator<Size>`, `releaseAllThreadMagazines()`, `getTotalUnusedAllocatedMemory()`, `countedNew()`, `countedDelete()`, `keepalive_allocator::ActiveScope`, `allocateAndMaybeKeepalive()`, `freeOrMaybeKeepalive()`, `nextFastAllocatedSize()`, `FastAllocated<Object>`, `allocateFast()`, `freeFast()`, `allocateFast4kAligned()`, and `freeFast4kAligned()`.

## Control Flow
Small fixed sizes use per-thread magazines and global refill/release paths. `FastAllocated` routes class `new/delete` to size classes up to 256 bytes and counted allocation above that. Generic `allocateFast()` selects a size class by requested bytes. Aligned 4K helpers use size-class allocators for supported sizes unless jemalloc is enabled.

## State And Persistence Behavior
Allocator state includes thread-local magazine data, global allocator data, optional instrumentation maps, sampled backtrace maps, counters, and keepalive tracked allocations. No user data persists after release, except keepalive mode can retain invalidated memory for wipe-policy tests.

## Dependencies And Integration Points
It depends on Flow platform allocation, `Error`, `SimpleCounter`, config macros, thread primitives, Bob Jenkins hash, Valgrind/ASAN hooks, and optional Linux backtrace APIs. It is used by actors, callbacks, `IndexedSet`, packet queues, and coroutine frames.

## Risks And Edge Cases
Static thread-local destruction order is explicitly risky. `FastAllocated` aborts if allocation size differs from `sizeof(Object)`. Size-class mismatch on free corrupts allocator state. Keepalive scope permits only one active instance and requires tracked allocations to follow strict lifetime rules.

## Test Signals
Allocator stress tests, per-size allocate/free loops, cross-thread magazine release, instrumentation builds, Valgrind/ASAN runs, 4K alignment checks, keepalive wipe tests, and out-of-memory handling provide coverage.
