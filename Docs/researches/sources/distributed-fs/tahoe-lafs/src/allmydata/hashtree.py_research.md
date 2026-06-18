# sources/distributed-fs/tahoe-lafs/src/allmydata/hashtree.py

## Purpose
Provides Tahoe's Merkle hash tree primitives for immutable uploads/downloads: complete trees for producing roots/proofs, and incomplete trees for incrementally validating hashes and leaves from untrusted storage servers.

## Important APIs, Types, And Functions
`roundup_pow2(x)` expands leaf counts to the next power of two. `CompleteBinaryTreeMixin` supplies array-indexed complete-tree navigation: `parent`, `lchild`, `rchild`, `sibling`, `needed_for`, `depth_first`, `dump`, `get_leaf_index`, and `get_leaf`.

`depth_of(i)`, `empty_leaf_hash(i)`, and `pair_hash(a, b)` encapsulate tree-level math and tagged hashing. `HashTree(L)` builds a full list-backed Merkle tree from leaf hashes, padding to a power of two with deterministic empty-leaf hashes. `HashTree.needed_hashes(leafnum, include_leaf=False)` returns proof nodes excluding root by default.

`IncompleteHashTree(num_leaves)` starts as a same-shaped list of `None`. `needed_hashes()` asks only for missing proof nodes. `set_hashes(hashes=None, leaves=None)` atomically adds internal hashes and/or leaf-indexed hashes, verifies them up to a known or computed root, and rolls back all newly inserted hashes on `BadHashError` or `NotEnoughHashesError`.

## Control Flow
Complete tree construction pads leaves, computes parent rows bottom-up with `pair_hash`, reverses rows, and flattens them into the heap-style tree list. Proof calculation walks from a leaf node toward root collecting siblings.

Incomplete validation first normalizes `leaves` into tree indices and checks for conflicting caller-supplied hashes. It provisionally inserts new hashes, tracks inserted nodes by depth, then validates from deepest level to root. For each pending node it requires a sibling, computes the parent from sorted left/right children, verifies or inserts the parent, and marks sibling coverage as validated. On failure it clears every hash inserted during the call before re-raising.

## State And Persistence
No disk persistence. Both tree classes are mutable `list` subclasses. `HashTree` stores complete bytes for every node. `IncompleteHashTree` progressively stores validated bytes or `None`, with `first_leaf_num` defining the leaf offset. Atomic rollback in `set_hashes()` is the key state invariant.

## Dependencies And Integration Points
Uses Tahoe `mathutil`, `base32`, and `hashutil.tagged_hash/tagged_pair_hash`. It is used by immutable encoding to build block, share, and ciphertext hash trees; immutable checker/downloader paths use `IncompleteHashTree` to validate UEB-derived roots, share hash chains, block hash chains, and ciphertext segment hashes.

## Risks And Edge Cases
Tree construction assumes at least one leaf; zero leaves would make `roundup_pow2(0)` return 1 but indexing semantics are not meaningful. The list subclass exposes mutation operations that can violate invariants if external callers modify entries directly. `set_hashes()` insists on enough data to validate every new hash, so callers must include a trusted root or already have one. Performance is covered by tests because earlier implementations had quadratic behavior.

## Test Signals
`src/allmydata/test/test_hashtree.py` covers complete tree proofs, incomplete-tree validation, failure rollback, bad/conflicting hashes, insufficient hashes, odd leaf counts, and performance behavior. Downloader corruption tests in `test_download.py` also exercise hash-tree failure paths.
