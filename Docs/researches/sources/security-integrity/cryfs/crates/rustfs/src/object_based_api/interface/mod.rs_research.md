# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/mod.rs

Purpose: module facade for object-based filesystem traits.

Important APIs: declares `device`, `dir`, `file`, `node`, `open_file`, and `symlink`; re-exports `Device`, `Dir`, `File`, `Node`, `OpenFile`, and `Symlink`.

Control flow and state: no runtime behavior.

Dependencies and integration: consumed by `object_based_api/mod.rs`, adapters, utilities, and filesystem implementations.

Risks and tests: this is the public object API boundary; changes alter implementation requirements for downstream filesystems.
