# sources/security-integrity/cryfs/crates/check/src/error/node_missing.rs

Purpose: This file defines the corruption error for a referenced node id that is absent from the blockstore.

Important APIs and flow: `NodeMissingError` stores `node_id` and `referenced_as: BTreeSet<NodeAndBlobReference>`. `new` asserts at least one reference. `Display` renders a `NodeErrorDisplayMessage` with node info `Missing`.

State and persistence: It is deterministic diagnostic data. References capture whether the missing node was a root node of a blob, an inner node, or a leaf node, and whether the owning blob is reachable or unreachable.

Dependencies and integration: It is emitted by `CheckUnreferencedNodes` and asserted by runner/blob checks when a missing blob root node is observed. It is included in `CorruptedError`.

Risks and test signals: Extensive unit tests cover missing nodes in unreachable blobs, file/dir/symlink root and child nodes, and multiple references. The constructor prevents semantically invalid "missing but unreferenced" errors.
