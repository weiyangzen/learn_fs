# File Research: sources/virtualization/virtiofsd/src/passthrough/util.rs

This file contains small passthrough helpers for fd opening, fd path discovery, errno construction, and shared-root-relative path handling.

Open helpers:
- `openat()` wraps `libc::openat()` with `CString` conversion and returns `File`.
- `openat_verbose()` adds path context to errors and is intended for internal setup, not guest-returned errors.
- `reopen_fd_through_proc()` opens `/proc/self/fd/{fd}` with adjusted flags, clearing `O_NOFOLLOW` because the proc entry is a symlink.
- `is_safe_inode()` returns true only for regular files and directories.

Errno helpers:
- `ebadf()`, `einval()`, and `erofs()` construct common raw OS errors.

FD path discovery:
- `FdPathError` distinguishes readlink failure, too-long symlink, invalid C string, non-file proc link targets, and deleted targets.
- `get_path_by_fd()` reads the `/proc/self/fd/{fd}` symlink, rejects targets whose pre-slash segment contains `:`, and rejects targets ending in `" (deleted)"`.
- `printable_fd()` returns a path through proc when possible or a `{fd:N}` placeholder.

Relative path handling:
- `relative_path(path, prefix)` strips a byte prefix from a C string path, removes leading slashes from the remainder, and returns the remaining `CStr`.

Interactions:
- Used by `passthrough/mod.rs` for opening and reopening files.
- Used by `inode_store.rs` and `proc_paths.rs` for migration path discovery.
- Used by `mount_fd.rs` and `serialization.rs` through `openat()` and `relative_path()`.

Edge cases and risks:
- `get_path_by_fd()` treats anonymous or special proc targets as non-file paths and treats deleted paths as invalid for migration.
- `relative_path()` is a byte-prefix operation rather than a component-aware path check; callers that need strict directory containment should verify the resolved inode path through subsequent lookup.
- `openat_verbose()` can clobber raw errno context, which is why the file warns not to use it for errors returned directly to the guest.
