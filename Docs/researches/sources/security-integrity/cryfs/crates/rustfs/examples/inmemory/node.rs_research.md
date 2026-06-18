# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/node.rs

Purpose: Implements the in-memory sum type for file, directory, and symlink nodes.

Important APIs/types/functions: `InMemoryNodeRef` variants wrap the concrete refs. `clone_ref` preserves shared inode ownership. The `Node` impl provides `as_file`, `as_dir`, `as_symlink`, `getattr`, and `setattr` dispatch.

Control flow: type conversions return type-specific errors where implemented. Metadata operations dispatch to the underlying ref and pass through optional size and timestamp changes.

State and persistence behavior: no state beyond cloned `Arc` refs to memory-only inodes.

Dependencies and integration points: central node type for `InMemoryDevice` and directory entries.

Risks: symlink-to-file conversion returns `UnknownError` instead of a precise error. Timestamp semantics are marked TODO. Size setattr validity depends on the target type implementation.

Test signals: type-dispatch tests should assert correct errors for wrong node kind and metadata propagation for each variant.
