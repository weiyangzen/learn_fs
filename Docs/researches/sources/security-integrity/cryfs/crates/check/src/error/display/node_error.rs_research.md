# sources/security-integrity/cryfs/crates/check/src/error/display/node_error.rs

Purpose: This module provides shared display formatting for node-related corruption errors, including how a node is referenced through a blob.

Important APIs and flow: `NodeErrorDisplayMessage` combines an `ErrorTitle` and `ErrorDisplayNodeInfo`. Formatting writes each `NodeAndBlobReference`, the node id, and observed node info. Helpers render root nodes, non-root inner nodes, non-root leaf nodes, reachable blob context, and unreachable blob context.

State and persistence: It owns no persistent state. It formats iterators over reference sets and value enums.

Dependencies and integration: It depends on `BlockId`, `BlobType`, `BlobReferenceWithId`, `MaybeBlobReferenceWithId`, `MaybeNodeInfoAsSeenByLookingAtNode`, and `NodeAndBlobReference`. All node error `Display` implementations use it.

Risks and test signals: Formatting is intentionally detailed and multi-line. Many node error tests assert exact ANSI-stripped output, so display changes require synchronized test updates. Reachable/unreachable blob context is important for diagnosing orphaned trees.
