# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/device.rs

Purpose: root trait for object-based filesystem implementations.

Important APIs: associated types `Node`, `Dir<'a>`, `Symlink<'a>`, `File<'a>`, and `OpenFile`; optional `on_operation`; required `rootdir`, `rename`, and `statfs`; default path-based `lookup`.

Control flow and state: default `lookup` starts from `rootdir`, converts to node, walks intermediate path components as directories, calls `lookup_child`, and async-drops each previous node before continuing. Root path returns root node directly.

Dependencies and integration: object adapters consume this trait. It depends on `AsyncDrop`, `AsyncDropGuard`, `AbsolutePath`, and `with_async_drop_2`.

Risks and tests: `lookup` performs repeated directory conversions and has TODOs for avoiding extra drops/lookups. The `rename` method is retained mainly for fuse-mt and may be removed once low-level-style dir operations cover that backend.
