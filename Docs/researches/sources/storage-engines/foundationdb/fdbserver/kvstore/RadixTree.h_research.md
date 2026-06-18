# sources/storage-engines/foundationdb/fdbserver/kvstore/RadixTree.h

## Purpose
This header implements an in-memory compressed radix tree mapping `StringRef` keys to `StringRef` values. It is shaped like an `IKeyValueContainer` alternative: ordered iteration, `find`, `lower_bound`, `upper_bound`, insert/replace, erase, and approximate memory accounting through `sumTo(end())`.

## Important APIs, Types, And Functions
The public type is `radix_tree`. Public operations are `size`, `empty`, `clear`, `find`, `begin`, `end`, `previous`, `insert`, `erase`, `lower_bound`, `upper_bound`, and `sumTo`. The nested `iterator` carries a raw node pointer and reconstructs full keys via `getKey(uint8_t* content)` by walking parent prefixes.

Internal node storage uses a common `node` header with bitfields for leaf/fixed/inline state, compressed key fragment, depth, arena, and parent pointer. `leafNode` stores the value; `internalNode` stores sorted child pairs in a vector; `internalNode4` stores up to three sorted children in fixed arrays before upgrading to vector storage. `radix_substr`, `radix_join`, and `radix_constructStr` handle `StringRef` slicing/copying with arena-backed storage. `append`, `prepend`, `add_child`, `delete_child`, `find_node`, `descend`, and child access helpers implement the radix operations.

## Control Flow
Lookup starts at `m_root` and descends by comparing the next key byte and compressed prefix fragment. `find_node` returns an exact leaf, the deepest internal match, or the first node whose compressed fragment diverges. `insert` creates the root on demand, appends a new leaf under the current internal node, replaces an exact leaf value if allowed, or calls `prepend` to split a diverging existing node under a new internal prefix node. Child arrays remain sorted by first byte, so iteration can use first/last descendant traversal and parent/sibling walks.

Erase removes a leaf from its parent, decrements accounting, and if the parent is not root and now has only one child, merges the parent prefix with the remaining child's prefix, replaces the parent in its grandparent, and deletes the parent. Range erase first snapshots node pointers to avoid invalidating iteration during deletion.

## State And Persistence Behavior
The tree is process-local and has no disk persistence. It manually owns all nodes through `new` and deletes subtrees through internal-node destructors or explicit erase paths. Short compressed keys and values are stored inline in a union sized to `sizeof(StringRef)`; longer fragments are copied into `Arena` objects stored in the node or leaf. `m_size`, `m_node`, `inline_keys`, and `total_bytes` track entry counts and memory estimates.

## Dependencies And Integration Points
The header depends on Flow `StringRef`, `Arena`, `FastAllocated`, and assertion macros, plus `IKeyValueContainer.h` for the common container interface shape. It is header-only, so changes affect compile units including it.

## Risks
Manual memory and type-punning make this code sensitive to node-state invariants. `internalNode4`'s destructor does not delete children, so deleting an `internalNode4` subtree directly would leak unless children were moved or removed first; most paths delete through vector nodes or transform fixed nodes carefully. `radix_tree::~radix_tree` is empty, so callers must call `clear()` or accept leaked tree storage at destruction. `previous(end())` assumes `m_root` is not null. Several dummy interface methods assert false. Memory accounting is approximate and maintained by many branch-specific adjustments, which can drift if child conversion or merge logic changes. Iterators are raw pointers and become invalid after mutation.

## Test Signals
Useful tests should cover empty tree operations, insertion of prefix-related keys, replacement with and without `replaceExisting`, forward and reverse iteration, lower/upper bound around missing prefixes, erase of leaves that trigger parent merge, range erase, long keys/values that require arenas, child-array upgrade from `internalNode4` to vector, and memory-accounting invariants before and after `clear`.
