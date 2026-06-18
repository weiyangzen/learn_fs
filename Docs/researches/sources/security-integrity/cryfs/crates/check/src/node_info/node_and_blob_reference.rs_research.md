# sources/security-integrity/cryfs/crates/check/src/node_info/node_and_blob_reference.rs

Purpose: `NodeAndBlobReference` describes how a node is referenced, including the blob context that owns the data tree.

Important APIs and flow: Variants represent root nodes with `BlobReferenceWithId`, non-root inner nodes with maybe-reachable blob context, depth, and parent node id, and non-root leaf nodes with maybe-reachable blob context and parent id. `blob_info(self)` extracts owning blob context. `node_info(&self)` extracts `NodeReference`. The `From<NodeAndBlobReferenceFromReachableBlob>` implementation converts reachable traversal context into the general diagnostic enum.

State and persistence: It is immutable reference metadata stored in error sets and reference checkers.

Dependencies and integration: It depends on `BlockId`, `NonZeroU8`, `BlobReferenceWithId`, `MaybeBlobReferenceWithId`, `NodeReference`, and `NodeAndBlobReferenceFromReachableBlob`. Display helpers render each variant.

Risks and test signals: `blob_info(self)` consumes self, which is appropriate for conversion but requires cloning in callers that need to retain the full value. Unit tests verify conversion preserves both node and blob info.
