# sources/security-integrity/cryfs/crates/check/src/error/node_referenced_multiple_times.rs

Purpose: This file defines the corruption error for a data node id referenced from more than one parent or blob root.

Important APIs and flow: `NodeReferencedMultipleTimesError` stores `node_id`, `node_info: MaybeNodeInfoAsSeenByLookingAtNode`, and `referenced_as: BTreeSet<NodeAndBlobReference>`. `new` asserts at least two references. `Display` delegates to `NodeErrorDisplayMessage`.

State and persistence: It captures both observed node state and all incoming references. The `Maybe` node info allows duplicate references to missing or unreadable nodes to be reported with context.

Dependencies and integration: It is emitted by `CheckUnreferencedNodes` and asserted by the runner when its processed-node tracker sees a node id again with stable observed contents.

Risks and test signals: Tests cover missing, unreadable, inner, leaf, root-node references, reachable/unreachable owners, and many references. Because `BTreeSet` orders enum variants, display order is deterministic but tied to derived ordering.
