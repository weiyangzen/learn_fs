# sources/security-integrity/cryfs/crates/rustfs/src/high_level_api/interface.rs

Purpose: path-oriented asynchronous filesystem trait roughly matching FUSE operations while addressing nodes by absolute path and optional file handle.

Important APIs: response structs `AttrResponse`, `OpenResponse`, `OpendirResponse`, and `CreateResponse`; trait `AsyncFilesystem` with lifecycle, metadata, creation/deletion, rename/link, file I/O, directory I/O, statfs, xattr, access, and create operations.

Control flow and state: the trait has no implementation state. Methods receive `RequestInfo` by value, path references, typed handles, typed sizes/modes, and callbacks for borrowed read buffers. `read` returns the callback result to enforce callback invocation.

Dependencies and integration: implemented by `ObjectBasedFsAdapter` for `Device` implementations and consumed by the `fuse_mt` backend adapter. Uses common types and `cryfs_utils::path::AbsolutePath`.

Risks and tests: many raw parameters remain unwrapped (`flags`, lock owners, xattr flags). Some operations are expected to return `FsError::NotImplemented`. Tests currently focus on low-level mounted mkdir behavior rather than this trait directly.
