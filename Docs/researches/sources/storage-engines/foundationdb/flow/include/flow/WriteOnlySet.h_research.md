# sources/storage-engines/foundationdb/flow/include/flow/WriteOnlySet.h

## Purpose
Declares lock-free sampling containers under `ENABLE_SAMPLING`, primarily for copying actor lineage references while writers insert/remove concurrently.

## Important APIs, Types, And Functions
`WriteOnlySet<T, IndexType, CAPACITY>` exposes `insert`, `erase`, `replace`, and weakly consistent `copy`. It uses atomic pointer words, a lock-free free-index queue, and a deferred free-list. `WriteOnlyVariable` is a capacity-one wrapper. `ActorLineageSet` aliases `WriteOnlySet<ActorLineage, unsigned, 1024>`.

## Control Flow
Insert consumes a free index and stores a refcounted pointer. Erase removes and decrements immediately or defers when a copy has locked the pointer bit. Copy traverses entries, locks stable pointers, increments references, and drains deferred frees.

## State And Persistence Behavior
Process-local sampling state only. No persistence. The low pointer bit is used as a lock flag, requiring pointer alignment.

## Dependencies And Integration Points
Depends on Flow reference-counting and `boost::lockfree::queue`. Integrated with `INetwork::getActorLineageSet()` and actor lineage profiling.

## Risks And Edge Cases
Compiled only with `ENABLE_SAMPLING`. Fixed capacity means insert can return `npos`. `copy` is explicitly not a snapshot. Pointer alignment and lock-free atomic guarantees are required for correctness.

## Test Signals
Capacity failure, erase/replace refcounts, concurrent copy with erase, deferred cleanup, variable replacement, and lineage sampling under load.
