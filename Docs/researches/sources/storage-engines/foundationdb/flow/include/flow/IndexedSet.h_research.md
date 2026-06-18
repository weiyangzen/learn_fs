# sources/storage-engines/foundationdb/flow/include/flow/IndexedSet.h

## Purpose
`IndexedSet.h` implements an AVL-tree ordered set with per-node metric totals, rank-by-metric lookup, range-sum queries, range erase, and a `Map` wrapper with flexible compatible-key lookup.

## Important APIs, Types, And Functions
Important types are `IndexedSet<T,Metric>`, nested `Node`, iterators, `NoMetric`, `MapPair`, and `Map<Key,Value,Pair,Metric>`. APIs include insert/addMetric/erase/eraseAsync/find/lower_bound/upper_bound/lastLessOrEqual/index/getMetric/sumTo/sumRange/testonly balance checks, plus map-style `operator[]`, `get()`, and `clearAsync()`.

## Control Flow
Insertion descends by `compare()`, replaces existing nodes when requested, updates ancestor totals, and rotates to maintain AVL balance. `index(metric)` walks subtree totals to find the first item whose cumulative metric exceeds the target. Range erase finds a common subtree root, half-erases left/right portions, rebalances upward, removes the root, and frees detached forests synchronously or through `ISFreeNodes()` yielding every 1000 nodes.

## State And Persistence Behavior
Each node stores data, balance, subtree metric total, children, and parent. Set state is the root pointer. `Map` stores an `IndexedSet<MapPair,...>`. No disk persistence exists, but callers may rely on deterministic ordering and metric sums.

## Dependencies And Integration Points
It depends on `Arena`, `Platform`, `FastAlloc`, `Trace`, `Error`, `Deque`, Flow futures/yield, and global `compare()` overloads. It is used by memory storage and other ordered in-memory indexes requiring sums.

## Risks And Edge Cases
Metric overflow is undefined by contract. Custom `T` must provide a total order and compatible `compare()`. Range erase is complex and easy to break around balance/total updates. Async erase removes items synchronously but delays memory freeing, so iterators to erased nodes become invalid immediately.

## Test Signals
Randomized differential tests against `std::map` plus prefix sums, AVL invariant checks after insert/replace/delete/range delete, compatible-key lookup, metric overflow boundaries, async erase yielding, map wrapper behavior, and sanitizer runs for detached forest freeing are key.
