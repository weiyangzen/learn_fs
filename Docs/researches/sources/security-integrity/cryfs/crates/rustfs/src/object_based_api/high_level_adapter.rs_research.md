# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/high_level_adapter.rs

Purpose: adapts object-based `Device`, `Dir`, `File`, `OpenFile`, `Node`, and `Symlink` traits into the high-level path-based filesystem API.

Important APIs: `ObjectBasedFsAdapter::new`, `trigger_on_operation`, test-only `reset_cache_after_setup`, `Debug`, `AsyncFilesystem` impl, and `AsyncDrop` impl.

Control flow and state: stores delayed filesystem initialization in `Arc<RwLock<AsyncDropGuard<MaybeInitializedFs<Fs>>>>` and open files in `OpenFileList`. `init` constructs the device using request uid/gid. Most operations call `trigger_on_operation`, then either operate on an open file handle or resolve a path through `Device::lookup`. Path-splitting operations locate the parent directory and call child creation/removal methods. `read` uses the callback after fetching `Data`; `release` removes and async-drops the open file. `readdir` synthesizes self and parent references.

Dependencies and integration: used by the fuse-mt object backend. It relies on `with_async_drop_2` for deterministic guard release and common high-level response types.

Risks and tests: many operations are unimplemented: macOS utimens, mknod, link, xattrs, fsyncdir. `opendir` uses `FileHandle::MAX` as a dummy. Several TODOs mention missing path precondition checks, unwraps, and rename overwrite semantics.
