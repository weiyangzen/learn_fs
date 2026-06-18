# sources/security-integrity/cryfs/crates/check/src/error/node_unreadable.rs

Purpose: This file defines the corruption error for a node block that exists in the enumerated store but cannot be read as a data node.

Important APIs and flow: `NodeUnreadableError` stores `node_id` and a possibly empty `referenced_as` set. `new` constructs the error, and `Display` renders node info `Unreadable` through the shared node display helper.

State and persistence: The error is immutable diagnostic state. Empty references are allowed for unreadable nodes found in unreachable scans with no readable parent references.

Dependencies and integration: It is emitted by `CheckUnreferencedNodes` and used in runner/check assertions. A TODO notes the underlying load error is not yet stored.

Risks and test signals: Tests cover unreferenced unreadable nodes, root references, inner/leaf references, reachable and unreachable owners, and many-reference formatting. Lack of root-cause error details can limit low-level repair guidance.
