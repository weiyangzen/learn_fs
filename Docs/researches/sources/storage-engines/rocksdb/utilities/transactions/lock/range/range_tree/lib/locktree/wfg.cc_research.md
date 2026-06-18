# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/wfg.cc

## Purpose
`wfg.cc` implements a wait-for graph used by `lock_request` to detect transaction deadlocks among pending lock requests.

## Important APIs, Types, And Functions
Implemented methods include `create()`, `destroy()`, `add_edge()`, `node_exists()`, `cycle_exists_from_txnid()`, `apply_nodes()`, `apply_edges()`, node lookup/creation helpers, comparator, and `node::alloc/free`.

## Control Flow
`add_edge(a,b)` creates both nodes if missing and inserts `b` into `a`'s edge set. Cycle detection starts from a target node, depth-first traverses outgoing edges, marks visited nodes to avoid repeated recursion, and reports nodes on the discovered cycle through an optional callback while unwinding.

## State And Persistence Behavior
The graph is transient per deadlock check. It owns OMT nodes; each node owns a `txnid_set` of outgoing edges and a temporary `visited` flag. `destroy()` frees every node and edge set.

## Dependencies
It uses `db.h` error codes, memory macros, OMT, transaction ID sets, and invariants.

## Integration Points
`lock_request::build_wait_graph()` recursively adds edges from the current blocked request and other pending blockers, then calls `cycle_exists_from_txnid()`.

## Risks And Edge Cases
The graph only includes blockers that themselves have pending requests, so it detects wait cycles rather than all conflict relationships. Recursive DFS depth grows with wait-chain length. Reporter callbacks run during traversal and must tolerate partial cycle ordering.

## Test Signals
Deadlock tests should cover simple two-node cycles, longer cycles, acyclic chains, duplicate edges, and reporter callback contents. Range-lock timeout tests exercise the no-cycle path.
