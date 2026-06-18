# sources/user-network-fs/nfs-ganesha/src/avl/splay.c

Purpose: Implements an intrusive top-down threaded splay tree, optimizing repeated access by rotating searched keys near or to the root.

Important APIs/types/functions: Exports `splaytree_first()`, `splaytree_last()`, `splaytree_next()`, `splaytree_prev()`, `splaytree_lookup()`, `splaytree_insert()`, `splaytree_remove()`, `splaytree_replace()`, and `splaytree_init()`. Internal helpers manage thread/link tagging, subtree extremes, rotations, and `do_splay()`.

Control flow: `do_splay()` performs top-down splaying with temporary left/right assembly roots until it finds the key or closest terminal position, then reassembles the tree with the chosen root. Lookup splays and returns root only on exact match. Insert splays around the new node's key, then attaches the previous root and one side subtree under the new node while updating first/last. Remove splays the target to root, then joins left and right subtrees. Replace splays the old node, asserts it is root, and copies node contents into the replacement.

State and persistence behavior: Intrusive volatile state only; no allocation. Threaded predecessor/successor pointers are encoded either with low-bit tags or explicit booleans.

Dependencies and integration points: Uses shared declarations from `avltree.h`; callers provide comparators and node storage.

Risks: `splaytree_remove()` and `splaytree_replace()` assert the target is present after splaying, so misuse is fatal in debug and corrupting in release. Splay trees have amortized bounds but individual operations can be expensive. Thread tagging has the same alignment assumptions as `bst.c`.

Test signals: Access locality tests showing root changes, randomized insert/lookup/remove with inorder validation, endpoint maintenance, missing-key lookup leaving nearest root, replacement, and 32-bit/no-tag builds.
