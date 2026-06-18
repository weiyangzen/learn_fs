# sources/security-integrity/cryfs/crates/check/src/node_info/node_reference.rs

Purpose: `NodeReference` records how a node is expected to look based on the parent reference that points to it.

Important APIs and flow: Variants are `RootNode`, `NonRootInnerNode { depth, parent_id }`, and `NonRootLeafNode { parent_id }`.

State and persistence: It is traversal/reference metadata, not direct observed node state. The runner derives it when descending data-node trees.

Dependencies and integration: It depends on `BlockId` and `NonZeroU8`, and is embedded in `NodeAndBlobReferenceFromReachableBlob`.

Risks and test signals: Correct depth computation is critical; the runner computes child depth by subtracting one and treating zero as leaf.
