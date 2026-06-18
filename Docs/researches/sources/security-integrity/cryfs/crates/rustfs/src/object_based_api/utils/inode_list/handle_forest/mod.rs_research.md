# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/mod.rs

Purpose: module facade for inode-list forest internals.

Important APIs: declares `delayed_handle_release`, `handle_forest`, and `node`; re-exports `DelayedHandleRelease`, `GetChildOfError`, `HandleForest`, `MakeOrphanError`, `MoveInodeError`, `MoveInodeSuccess`, `TryInsertError`, and `TryRemoveResult`.

Control flow and state: no runtime behavior.

Dependencies and integration: consumed by `inode_list/mod.rs`.

State and persistence behavior: no state is stored here, but the exported types are the state-management vocabulary used by `InodeList` for parent/child topology, orphan handling, move handling, and delayed handle reuse. Keeping `node` private forces mutations through `HandleForest`, preserving invariants around bidirectional edges and async-drop ownership.

Risks and tests: intentionally exposes selected internals within the utility layer while keeping `node` private. A re-export mistake could either leak low-level mutable internals or hide error types needed by `InodeList` to translate forest failures into filesystem errors and panics.
