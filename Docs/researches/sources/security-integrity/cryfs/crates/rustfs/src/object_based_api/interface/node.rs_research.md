# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/node.rs

Purpose: common object interface for any filesystem node.

Important APIs: associated `Device`; conversions `as_dir`, `as_file`, `as_symlink`; `getattr`, `setattr`, and `fsync`.

Control flow and state: adapters first load nodes, then downcast to a concrete object kind via async methods. `setattr` accepts optional mode, uid, gid, size, atime, mtime, and ctime.

Dependencies and integration: used by both adapters, inode list, and test cache flush. Depends on `AsyncDropGuard`, typed attrs, ids, mode, and sizes.

Risks and tests: type mismatch errors must be reported by implementors. Optional setters require careful partial-update semantics and persistence ordering.
