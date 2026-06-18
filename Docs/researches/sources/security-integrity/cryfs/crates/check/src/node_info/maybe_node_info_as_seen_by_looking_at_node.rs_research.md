# sources/security-integrity/cryfs/crates/check/src/node_info/maybe_node_info_as_seen_by_looking_at_node.rs

Purpose: This enum extends direct node observation info with a `Missing` state for diagnostics.

Important APIs and flow: Variants are `Missing`, `Unreadable`, `InnerNode { depth }`, and `LeafNode`. `From<NodeInfoAsSeenByLookingAtNode>` maps observed unreadable/inner/leaf values into this superset.

State and persistence: It is immutable diagnostic state included in node errors where the node may be missing.

Dependencies and integration: It depends on `NonZeroU8` and `NodeInfoAsSeenByLookingAtNode`. Display helpers use it to render node info text.

Risks and test signals: Inner-node depth is preserved, but child ids are not included in final diagnostics.
