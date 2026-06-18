# sources/security-integrity/cryfs/crates/rustfs/src/low_level_api/interface.rs

Purpose: inode-oriented asynchronous filesystem trait aligned closely with FUSE low-level operations.

Important APIs: reply structs for entry, attr, open, write, create, lock, bmap, lseek, xtimes, and ioctl; `ReplyDirectory` and `ReplyDirectoryPlus` buffer traits; `ReplyDirectoryAddResult`; trait `AsyncFilesystemLL` with init/destroy, lookup/forget, metadata, readlink, mknod/mkdir/unlink/rmdir/symlink/rename/link, open/read/write/flush/release/fsync, opendir/readdir/readdirplus/releasedir/fsyncdir, statfs, xattrs, access, create, locks, bmap, ioctl, fallocate, lseek, copy range, and macOS operations.

Control flow and state: implementations control inode lifetime through lookup and forget. Directory reply traits let adapters stop when buffers are full. Callback-based read and readlink keep borrowed data lifetimes local.

Dependencies and integration: implemented by `ObjectBasedFsAdapterLL`; backend adapters translate fuser calls to this trait. Uses common typed wrappers and `PathComponent`.

Risks and tests: the trait includes many operations that the object adapter returns as `NotImplemented`. Numerous TODOs flag raw integer parameters and platform-specific semantics. `mkdir` tests exercise lookup, creation, errno mapping, and mounted fuser integration.
