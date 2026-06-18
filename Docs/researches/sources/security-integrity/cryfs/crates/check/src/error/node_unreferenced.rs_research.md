# sources/security-integrity/cryfs/crates/check/src/error/node_unreferenced.rs

Purpose: This file defines the corruption error for an existing node that is not referenced by any other node or blob.

Important APIs and flow: `NodeUnreferencedError` stores `node_id` and `node_info: NodeInfoAsSeenByLookingAtNode`. `new` constructs the value, and `Display` renders no references plus the observed node info.

State and persistence: It is immutable diagnostic data for orphaned nodes discovered during the all-block scan and unreachable-node checker.

Dependencies and integration: It is emitted by `CheckUnreferencedNodes` finalization when a seen node has an empty reference set. It is part of `CorruptedError`.

Risks and test signals: Unit tests cover unreadable, inner, and leaf node display. In the reachable-node checker this error is treated as an invariant violation, because reachable traversal should never discover a child without also seeing the parent reference.
