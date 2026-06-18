# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/backend_adapter.rs

Purpose: Adapts the high-level path-based `AsyncFilesystem` API to the synchronous `fuse_mt::FilesystemMT` trait.

Important APIs/types/functions: `BackendAdapter` stores `Arc<RwLock<AsyncDropGuard<Fs>>>` plus a Tokio runtime handle. `run_async` synchronously drives async filesystem methods and maps `FsError` to libc errno. The `FilesystemMT` impl covers init/destroy, metadata, node creation/removal, rename/link, open/read/write, flush/release/fsync, directory operations, statfs, xattrs, access, and create. Helpers convert attrs, node kinds, flags, paths, file handles, request info, statfs, and read callbacks.

Control flow: each FUSE call parses kernel inputs into CryFS path and scalar types, acquires a read guard for normal operations or write guard for destroy, awaits the high-level API, then converts replies. `read` uses a callback adapter because fuse_mt expects borrowed data through `ResultSlice`.

State and persistence behavior: adapter state is just the guarded filesystem object. `destroy` calls filesystem destroy and async drop. `Drop` safe-panics if destroy was not called first.

Dependencies and integration points: used by `backend/fuse_mt/mount.rs`; bridges `fuse_mt`, `fuser_fusemt`, `AsyncFilesystem`, and common rustfs types.

Risks: TODOs question concurrent `runtime.block_on`, FUSE precondition checking, symlink behavior, and incomplete flag support. Several conversions unwrap on size/handle assumptions. Invalid xattr UTF-8 maps to broad errors.

Test signals: backend integration tests should exercise all operations through a mounted filesystem, especially destroy-after-open, xattrs, read callback behavior, and flag parsing.
