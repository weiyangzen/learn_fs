# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/concurrent_tree.h

## Purpose
`concurrent_tree.h` declares a range-index abstraction whose nodes store non-overlapping lock ranges and whose `locked_keyrange` guard grants exclusive access to the subtree overlapping a requested range.

## Important APIs, Types, And Functions
`concurrent_tree` exposes `create(const comparator*)`, `destroy()`, `is_empty()`, and `get_insertion_memory_overhead()`. Nested `locked_keyrange` exposes `prepare()`, `acquire()`, `release()`, templated `iterate(F*)`, `add_shared_owner()`, `insert()`, `remove()`, and `remove_all()`.

## Control Flow
The access model is documented in the header: all users serialize at `prepare()`, then either acquire a narrower overlapping range or operate under the root-wide prepared state, then release. `iterate()` traverses the locked subtree and only visits ranges overlapping `m_range`.

## State And Persistence Behavior
The object embeds one root `treenode` so even an empty tree has a mutex. `locked_keyrange` stores pointers to the tree and currently locked subtree plus the represented `keyrange`. No durable storage is involved.

## Dependencies
It includes the comparator wrapper, `keyrange`, and `treenode`. Templates are intentionally expanded through inclusion in `locktree.cc`.

## Integration Points
This is the low-level concurrency primitive below `locktree`. Higher layers use it to make acquisition/release/escalation appear atomic with respect to overlapping ranges while allowing disjoint subtree operations.

## Risks And Edge Cases
The class does not enforce RAII, so exceptions or early returns can leak locks if callers do not release. The contract requires callers to avoid inserting overlapping ranges and to remove only existing exact ranges. Shared-owner updates require an exact keyrange match.

## Test Signals
All range-lock manager tests that acquire conflicting or non-conflicting ranges are integration signals. Structural behavior is also exercised by lock escalation, which iterates and rebuilds the whole tree.
