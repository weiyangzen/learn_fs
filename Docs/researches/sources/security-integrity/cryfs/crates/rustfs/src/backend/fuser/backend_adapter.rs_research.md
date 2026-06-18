# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/backend_adapter.rs

Purpose: Adapts the low-level inode-based `AsyncFilesystemLL` API to `fuser::Filesystem`.

Important APIs/types/functions: `BackendAdapter` stores a guarded filesystem and runtime. It provides many `run_async_reply_*` helpers for spawning async operations and replying with fuser reply types. The `Filesystem` impl covers init/destroy, lookup, forget, getattr/setattr, readlink, mknod/mkdir/unlink/rmdir/symlink/rename/link, open/read/write, flush/release/fsync, opendir/readdir/readdirplus/releasedir/fsyncdir, statfs, xattrs, access, create, locks, bmap, ioctl, fallocate, lseek, copy_file_range, and macOS extensions.

Control flow: most kernel callbacks clone request info and owned names/data, parse inode/file-handle/path-component inputs, spawn an async task on the provided runtime, call the low-level API, and complete the provided reply. Init/destroy use `run_blocking`, which runs on a short-lived thread if already inside a Tokio runtime to avoid nested `block_on` panics.

State and persistence behavior: adapter state is the async-drop guarded filesystem. Destroy invokes fs destroy and async drop; later operations detect dropped state and return `FilesystemDestroyed`.

Dependencies and integration points: used by `backend/fuser/mount.rs`; integrates fuser 0.17 with rustfs low-level API and directory reply traits.

Risks: many conversions use unwrap for size and signed/unsigned offsets. `OpenOutFlags` conversion is not implemented. Comments note inode generation uniqueness requirements for NFS, FUSE API drift, and copy minimization. All reply paths must reply exactly once.

Test signals: rustfs tests include fuser runner utilities. High-value tests cover every reply helper, dropped-filesystem operations, xattr size/data branches, directory full replies, lock/ioctl/fallocate paths, and init/destroy inside Tokio.
