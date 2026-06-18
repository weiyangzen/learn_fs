# sources/security-integrity/cryfs/crates/check/src/checks/utils/reference_checker.rs

Purpose: `ReferenceChecker` is a generic helper for tree/graph checks where each id may be seen directly and referenced by zero or more parents.

Important APIs and flow: It stores `HashMap<NodeId, (Option<SeenInfo>, Vec<ReferenceInfo>)>`. `mark_as_seen` records direct observation and panics if the same id is seen twice. `mark_as_referenced` appends incoming reference metadata. `finalize` consumes the map and yields `(id, seen_info, references)` for caller-specific error generation.

State and persistence: All state is in memory and scoped to one check instance. It preserves every reference in a `Vec`, so callers can distinguish zero, one, and multiple references.

Dependencies and integration: It is generic over hashable ids and metadata. `CheckParentPointers` uses it for blobs, and `CheckUnreferencedNodes` uses it for nodes.

Risks and test signals: The panic on duplicate seen ids enforces a runner invariant that each node/blob is processed once in the relevant checker. Duplicate references are allowed and intentionally represented for error reporting.
