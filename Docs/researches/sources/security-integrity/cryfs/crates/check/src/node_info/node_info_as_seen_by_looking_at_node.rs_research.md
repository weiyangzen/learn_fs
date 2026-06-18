# sources/security-integrity/cryfs/crates/check/src/node_info/node_info_as_seen_by_looking_at_node.rs

Purpose: This enum describes what was observed when loading a node directly.

Important APIs and flow: Variants are `Unreadable`, `InnerNode { depth: NonZeroU8 }`, and `LeafNode`.

State and persistence: It is value-only diagnostic state used by node checks and `NodeUnreferencedError`.

Dependencies and integration: It depends on `NonZeroU8` for inner depths. It converts into `MaybeNodeInfoAsSeenByLookingAtNode` in a sibling module.

Risks and test signals: It cannot represent missing nodes; callers use the `Maybe` wrapper when absence is possible.
