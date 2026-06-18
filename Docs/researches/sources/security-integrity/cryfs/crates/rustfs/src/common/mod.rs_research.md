# sources/security-integrity/cryfs/crates/rustfs/src/common/mod.rs

Purpose: central export module for shared RustFS types.

Important APIs: declares and re-exports typed IDs, errors, mode, attributes, byte counts, flags, stats, callbacks, request info, directory entries, atime behavior, and handle utilities. Feature gates expose handle pools and file handles only when FUSE backends are active.

Control flow and state: no runtime behavior. It determines which common types are visible to `lib.rs` and internal modules.

Dependencies and integration: every API layer imports from this module. `lib.rs` publicly re-exports most of these types for users implementing filesystems.

Risks and tests: feature-gated exports can produce API differences across builds. The module is source-tree alignment glue; mistakes here become public API breakage.
