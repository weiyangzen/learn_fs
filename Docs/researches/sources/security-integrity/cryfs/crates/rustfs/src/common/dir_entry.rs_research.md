# sources/security-integrity/cryfs/crates/rustfs/src/common/dir_entry.rs

Purpose: defines directory listing values shared by object and path adapters.

Important APIs: `DirEntry { name: PathComponentBuf, kind: NodeKind }` describes a real child. `DirEntryOrReference` wraps either `Entry`, `SelfReference`, or `ParentReference`.

Control flow and state: these are plain data structures. The high-level adapter synthesizes `.` and `..` as `SelfReference` and `ParentReference`; the low-level adapter writes those directly into reply buffers before ordinary entries.

Dependencies and integration: depends on `cryfs_utils::path::PathComponentBuf` and local `NodeKind`. `Dir::entries` returns `Vec<DirEntry>`, high-level `readdir` returns an iterator of `DirEntryOrReference`, and low-level `readdir` converts `DirEntry` into FUSE reply entries.

Risks and tests: correctness depends on `NodeKind` being accurate for each child. `DirEntryOrReference` avoids representing `.` and `..` as names, which reduces path-component validation risk.
