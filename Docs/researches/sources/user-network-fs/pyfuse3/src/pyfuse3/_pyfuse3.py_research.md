# sources/user-network-fs/pyfuse3/src/pyfuse3/_pyfuse3.py

Purpose: Provides the pure-Python part of pyfuse3: version discovery, public integer/bytes type aliases, an `async_wrapper` for Cython async functions passed to Trio, and the base `Operations` contract for filesystem implementations.

Important APIs/types/functions: Exports `Operations` and `async_wrapper`. Defines aliases `FileHandleT`, `FileNameT`, `FlagT`, `InodeT`, `ModeT`, and `XAttrNameT`. `Operations` exposes capability flags `supports_dot_lookup`, `enable_writeback_cache`, and `enable_acl`. Operation methods document and default to `FUSEError(errno.ENOSYS)` for lookup, getattr, setattr, readlink, create/remove/link/rename, open/read/write/flush/release/fsync, poll, opendir/readdir/releasedir/fsyncdir, statfs, xattrs, access, and create. `init`, `forget`, and `stacktrace` have non-request semantics.

Control flow: Filesystem authors subclass `Operations` and override only supported handlers. The native pyfuse3 layer dispatches kernel FUSE requests into these async methods. If a default handler raises `ENOSYS`, the FUSE kernel may stop calling that request type and use fallback behavior where available. `stacktrace` is triggered by a debug extended attribute and logs Python thread stacks.

State and persistence: The base class stores no per-instance state. It defines behavioral defaults and documentation for how implementers should manage kernel lookup counts, inode lifetime, write semantics, xattr errors, and cache invalidation.

Dependencies and integration points: Depends on `errno`, `logging`, importlib metadata, and types injected by the compiled extension. It is central to examples/tests because user filesystems subclass it.

Risks: Misimplementing the documented lookup-count and deferred-deletion contracts can cause stale inode exposure or premature deletion. The `TYPE_CHECKING` split means runtime names such as `FUSEError` are injected externally; import order and extension initialization matter.

Test signals: `test_fs.py` subclasses `pyfuse3.Operations`; `tmpfs.py` and example files rely on these contracts. API tests verify extension-level objects and copy behavior, not every default method.
