## sources/test-tools/filebench/fb_avl.h

### Purpose
`fb_avl.h` defines the public API and layout contract for Filebench's embedded AVL tree. It describes how callers embed `avl_node_t` in their own structures and use `avl_tree_t` plus comparator functions to maintain ordered sets.

### Important APIs, Types, And Functions
The key types are `avl_node_t`, `avl_tree_t`, and `avl_index_t`. Macros convert between embedded nodes and containing data (`AVL_NODE2DATA`, `AVL_DATA2NODE`), encode insertion cookies (`AVL_MKINDEX`, `AVL_INDEX2NODE`, `AVL_INDEX2CHILD`), and expose iteration helpers (`AVL_NEXT`, `AVL_PREV`). Function prototypes cover creation, lookup, insertion, removal, update, traversal, node count, empty check, bulk destruction, and final destroy.

### Control Flow
The header documents the expected usage sequence: create a tree with a comparator and offset, use `avl_find`/`avl_insert` or `avl_add`, traverse with first/last/next/previous, optionally use nearest-node queries, remove nodes, and destroy remaining nodes with `avl_destroy_nodes` before `avl_destroy`.

### State And Persistence
`avl_tree_t` holds the root pointer, comparator, embedded-node offset, node count, and user object size. `avl_node_t` stores child links and either explicit parent/child/balance fields or a packed parent-child-balance word on 64-bit builds. No persistence or allocation policy is included.

### Dependencies And Integration Points
The header includes `filebench.h` for shared types. `fileset.h` embeds `avl_node_t` in `filesetentry_t`, making this header part of the fileset public type contract.

### Risks
The macros rely on pointer arithmetic and correct `offsetof`-style offsets. On 64-bit builds they rely on pointer alignment to leave low bits available. The comparator must return exactly `-1`, `0`, or `1`, not arbitrary negative/positive values. The API places all locking responsibility on callers.

### Test Signals
Header-level checks should compile both packing branches where possible, verify offsets with embedded structs, and use static or runtime tests for iteration macros and `avl_index_t` encoding.
