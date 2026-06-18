## sources/test-tools/filebench/fb_avl.c

### Purpose
`fb_avl.c` is Filebench's generic embedded-node AVL tree implementation, adapted from Solaris. It supplies ordered-set primitives used by filesets to track free, existing, and non-existing entries by index.

### Important APIs, Types, And Functions
Core operations are `avl_create`, `avl_find`, `avl_insert`, `avl_insert_here`, `avl_add`, `avl_remove`, `avl_first`, `avl_last`, `avl_walk`, `avl_nearest`, `avl_update`, `avl_update_lt`, `avl_update_gt`, `avl_numnodes`, `avl_is_empty`, `avl_destroy_nodes`, and `avl_destroy`. The internal `avl_rotation` handles both single and double rotations by symmetry.

### Control Flow
Search descends by comparator results, requiring exact `-1`, `0`, or `1`. Insertion places a leaf at an `avl_index_t` returned by `avl_find`, then walks ancestors adjusting balance and performs at most one rotation. Removal swaps two-child nodes with an adjacent node, deletes a node with at most one child, then walks ancestors applying rotations until height stabilizes. Iteration is iterative and uses parent pointers rather than recursion.

### State And Persistence
Tree state lives in caller-owned `avl_tree_t` and embedded `avl_node_t` fields inside caller data structures. The AVL layer allocates no memory and persists nothing. Node parent/child/balance data is stored in separate fields on 32-bit builds and packed into low bits of the parent pointer on 64-bit builds.

### Dependencies And Integration Points
It includes `filebench.h` and `fb_avl.h`, using `boolean_t` and `filebench_log`. `fileset.c` uses AVL trees for membership indexes. Any caller must provide locking around mutations and usually around traversal if concurrent mutation is possible.

### Risks
Comparator contract violations are logged and can leave callers without a found node. There is no internal synchronization. Passing unaligned data on 64-bit builds is rejected because low pointer bits are used for metadata. `avl_destroy` only logs when the tree is non-empty; it does not free nodes. There are duplicated log lines in a few error paths, but they do not change behavior.

### Test Signals
Tests should insert, find, iterate, remove, update, and destroy nodes in sorted and random orders; verify node count and ordering after every operation; run 32-bit/64-bit layout builds if supported; and exercise duplicate insert and comparator-error handling.
