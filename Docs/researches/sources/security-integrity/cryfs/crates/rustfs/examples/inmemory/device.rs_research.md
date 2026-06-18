# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/device.rs

Purpose: Implements an in-memory object-based filesystem device and root traversal.

Important APIs/types/functions: `RootDir::new`, `_node`, and `load_node` maintain and traverse the root directory. `InMemoryDevice::new` constructs the root. The `Device` impl supplies associated node types, `rootdir`, path-level `rename`, and placeholder `statfs`.

Control flow: `load_node` walks an absolute path component by component, requiring every intermediate node to be a directory. Rename splits old/new paths, loads parents, and either renames within one directory or locks source and target directories in pointer order to avoid deadlock.

State and persistence behavior: all state is process memory under `Arc<Mutex<DirInode>>`. There is no persistence and async drop is a no-op.

Dependencies and integration points: used by `examples/inmemory/main.rs` through `ObjectBasedFsAdapterLL`. Integrates dir/file/symlink node refs and `cryfs_utils::lock_in_ptr_order`.

Risks: rename blocks all overwrites even though POSIX allows some cases. `statfs` is `todo!()` and will panic if called. Many error semantics are TODO-level approximations.

Test signals: useful example tests should exercise lookup traversal, cross-directory rename deadlock avoidance, invalid root rename, and statfs behavior once implemented.
