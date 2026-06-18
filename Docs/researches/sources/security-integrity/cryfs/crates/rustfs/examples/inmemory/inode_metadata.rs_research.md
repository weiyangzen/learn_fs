# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/inode_metadata.rs

Purpose: Shared helper for mutating in-memory inode metadata.

Important APIs/types/functions: `setattr` updates optional mode, uid, gid, atime, mtime, and ctime fields on a mutable `NodeAttrs` and returns the new attrs.

Control flow: applies each optional argument independently; absent fields keep previous values.

State and persistence behavior: memory-only metadata mutation. Size changes are handled by callers before this helper.

Dependencies and integration points: called by in-memory dir, file, and symlink inode implementations.

Risks: callers decide ctime semantics; comments elsewhere note ctime/atime/mtime updates are incomplete.

Test signals: simple unit tests should verify every optional field and no-op behavior with all `None`.
