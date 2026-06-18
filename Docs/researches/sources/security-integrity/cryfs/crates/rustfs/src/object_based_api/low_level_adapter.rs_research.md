# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/low_level_adapter.rs

Purpose: adapts object-based filesystems to the low-level inode-based API used by the `fuser` backend.

Important APIs: `ObjectBasedFsAdapterLL::new`, test-only cache reset/flush helpers, `trigger_on_operation`, inode access helpers, `_orphan_inode`, `_move_inode`, full `AsyncFilesystemLL` implementation, `Debug`, and `AsyncDrop`.

Control flow and state: holds delayed filesystem initialization, `InodeList`, `OpenFileList`, and `DirCache`. `init` constructs the filesystem, loads rootdir, and registers the root inode. `lookup` uses `InodeList::add_or_increment_refcount`, loading children through parent directories and returning attrs. `forget` decrements inode references. Create/mkdir/symlink add loaded children. Unlink/rmdir remove the underlying child, then orphan any loaded inode. Rename updates underlying dirs, then moves the inode forest if the child was loaded. Open/read/write/flush/release/fsync use file handles. Opendir/readdir/releasedir use directory handles and cached entries with careful offsets for `.` and `..`.

Dependencies and integration: core bridge for `RustfsFuserBackend`. Depends on `MaybeInitializedFs`, `InodeList`, `DirCache`, `OpenFileList`, `flatten_async_drop`, and low-level reply traits.

Risks and tests: many advanced operations return `NotImplemented`. Several unwraps and panics enforce invariants. Readdirplus, xattrs, locks, fallocate, ioctl, lseek, and copy range are incomplete. Existing `mkdir` tests exercise lookup and creation paths through this adapter and fuser.
