# File Research: sources/local-fs/f2fs-tools/fsck/sload.c

Implements `sload.f2fs`, which recursively loads a host directory tree into an existing F2FS image.

Key responsibilities:
- Scans host directories with `scandir()` while filtering `.` and `..`.
- Builds `struct dentry` records with name, image path, host full path, mode, uid/gid, size, mtime, file type, symlink target, and hardlink identity.
- Creates F2FS directories, regular files, and symlinks through `f2fs_mkdir()`, `f2fs_create()`, and `f2fs_symlink()`.
- Recursively calls `build_directory()` for subdirectories and calls `f2fs_build_file()` for regular file data.
- Supports Android `fs_config` / canned fs config when available, overriding uid/gid/mode/capabilities.
- Supports SELinux labeling through `selabel_lookup()` and `inode_set_selinux()`.
- Entry point `f2fs_sload()` initializes fsck state, configures SELinux/Android file config, flushes journals, initializes hardlink cache, builds the tree, labels root, updates current segment info, flushes SIT, and writes checkpoint.

Important dependencies:
- Depends on `fsck.h` for F2FS creation helpers and global `c`.
- Depends on `segment.c` for file content writing.
- Depends on `xattr.c` for SELinux xattr installation.
- Platform-gated: Windows builds stub `build_directory()` to return failure.

Behavioral notes:
- Host metadata is read with `lstat()` to avoid following symlinks.
- If `c.fixed_time == -1` and `c.from_dir` is set, source mtimes are preserved; otherwise fixed time is used.
- The function returns `0` at the end of `build_directory()` even after some internal `ret` paths have jumped to cleanup, so some per-entry failures may be reduced to logged/partial behavior depending on where they occur.
