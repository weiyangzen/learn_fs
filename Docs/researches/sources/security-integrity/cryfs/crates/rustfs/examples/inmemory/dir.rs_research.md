# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/dir.rs

Purpose: Implements in-memory directory inode state and the object-based `Dir` trait.

Important APIs/types/functions: private `DirInode` stores `NodeAttrs` and `HashMap<PathComponentBuf, InMemoryNodeRef>`. `InMemoryDirRef` wraps it in `Arc<Mutex<_>>` and exposes metadata, child lookup, setattr, rename, cloning, and inode access. The `Dir` impl handles lookup, rename/move, entries, create/remove directory, symlink, and file operations.

Control flow: directory mutations lock the inode mutex. Cross-directory moves lock two directories in pointer order. Entry creation checks occupied names before inserting. Directory listing maps stored node enum variants to `NodeKind`.

State and persistence behavior: entries and attributes are memory-only. Metadata size/link counts are simplistic; comments warn that exposing `entries_mut` could violate future invariants.

Dependencies and integration points: used by `InMemoryDevice`, `InMemoryNodeRef`, and file/symlink refs. It mirrors the object-based API contracts used by adapters.

Risks: POSIX overwrite behavior is incomplete. Mutex poisoning uses `unwrap`, so panics can cascade. Metadata timestamps and directory sizes are approximate.

Test signals: cover create/list/remove, duplicate names, same-dir and cross-dir rename, move overwrite rejection, and metadata updates.
