# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_hashtree.py

Purpose: tests complete and incomplete Merkle hash tree behavior in `allmydata.hashtree`. It verifies tree padding to powers of two, leaf indexing, authentication-path calculation, depth-first traversal, dump formatting, incremental hash insertion, validation failures, and performance expectations for large incomplete-tree updates.

Important APIs and types include `make_tree`, `Complete`, and `Incomplete`. The implementation under test includes `HashTree`, `IncompleteHashTree`, `depth_of`, `needed_hashes`, `get_leaf`, `get_leaf_index`, `parent`, `depth_first`, `dump`, `set_hashes`, `NotEnoughHashesError`, and `BadHashError`.

Control flow builds leaf hashes from `tagged_hash(b"tag", leaf)` and constructs trees of sizes 1, 3, 6, 8, 9, and 10,000. Complete-tree tests check root length, leaf values, index errors, a known base32-encoded seven-node tree, sibling hashes needed for leaves, and depth-first node/depth tuples. Incomplete-tree tests start with unknown nodes, add roots, chains, and leaves, and assert that insufficient, conflicting, or wrong internal hashes leave the tree unchanged or raise the right error before successful updates reduce future needed hashes.

State and persistence are in-memory lists/arrays of hashes. The important state behavior is transactional validation: failed `set_hashes` calls must not mutate the incomplete tree. The speed test builds a large complete tree, extracts all hashes needed to validate all leaves, and applies them to an incomplete tree to guard against old O(N^2) behavior.

Dependencies include base32 encoding for known-answer display, `tagged_hash` from hashutil, the `hashtree` module, and `SyncTestCase`. Integration points are immutable share/block/crypttext hash verification, where downloaders often receive partial hash chains and fill incomplete trees incrementally.

Risks covered include off-by-one leaf indexes, incorrect sibling-chain calculation with or without including the leaf, bad padding behavior for non-power-of-two leaf counts, mutation after failed verification, accepting conflicting hashes, wrong depth calculations, and algorithmic regressions on large trees. Residual risk is that the large speed test has no timing assertion; it is mainly a practical guard that would become visibly slow on old behavior.

Test signals include exact needed-hash sets, exact base32 known tree output, exact depth-first traversal tuple list, `IndexError`, `NotEnoughHashesError`, and `BadHashError` checks, unchanged incomplete-tree state after failure, successful leaf validation after chain insertion, and completion of a 10,000-leaf update.
