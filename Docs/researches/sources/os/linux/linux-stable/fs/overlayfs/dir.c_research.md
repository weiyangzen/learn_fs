# File Research: sources/os/linux/linux-stable/fs/overlayfs/dir.c

## Scope

This file implements overlayfs directory inode operations: create, mkdir, mknod, symlink, hardlink, unlink, rmdir, rename, tmpfile, whiteout handling, cleanup, temp object creation, opaque directory handling, redirect xattrs, credential overrides for creation, and parent/dentry state updates.

## Public And Internal APIs Covered

- Public helpers: `ovl_cleanup()`, `ovl_tempname()`, `ovl_cleanup_and_whiteout()`, `ovl_create_real()`, `ovl_create_temp()`.
- Creation paths: `ovl_create_upper()`, `ovl_create_over_whiteout()`, `ovl_create_or_link()`, `ovl_create_object()`, VFS callbacks `ovl_create()`, `ovl_mkdir()`, `ovl_mknod()`, `ovl_symlink()`, `ovl_link()`.
- Removal paths: `ovl_remove_upper()`, `ovl_remove_and_whiteout()`, `ovl_do_remove()`, `ovl_unlink()`, `ovl_rmdir()`.
- Rename paths: `ovl_set_redirect()`, `ovl_rename_start()`, `ovl_rename_upper()`, `ovl_rename_end()`, `ovl_rename()`.
- Tmpfile support: `ovl_tmpfile()`, `ovl_create_tmpfile()`.
- Operation table: `ovl_dir_inode_operations`.

## Control Flow And Behavior

- Temporary names are generated from an atomic counter and used in workdir/index operations.
- Whiteouts are created in workdir. A shared whiteout inode is reused through hardlinks until link creation fails with non-`EMLINK`, after which sharing is disabled.
- Cleanup removes temporary dentries with directory-aware unlink/rmdir wrappers and logs failures.
- Creating a real upper object dispatches by mode to create, mkdir, mknod, symlink, or hardlink. Directory creation validates inherited casefold state.
- Creation over a whiteout creates a temp object, applies mode/ACL adjustments, then renames over the whiteout. Directory creation over whiteout uses exchange plus cleanup to preserve whiteout semantics.
- Overlay creation first copies up the parent, gets write access, preallocates an overlay inode, initializes ownership, overrides creator credentials to the new inode uid/gid, creates or links the upper object, then instantiates the overlay dentry.
- Hardlink creation copies up the old object and new parent, starts nlink tracking, ensures metacopy hardlinks have redirects, and links the upper dentry into the new parent.
- Remove/rmdir checks merged directory emptiness, copies up the parent, starts nlink tracking, and either removes pure upper objects or replaces lower-positive objects with whiteouts.
- Directory clearing for non-empty merged whiteout cleanup creates an opaque temp directory, copies xattrs/attrs, exchanges it with the upper dir, cleans contained whiteouts, and drops the stale overlay dentry.
- Rename refuses unsupported flags, avoids copying up whole directory trees when redirects are unavailable, copies up source/target parents as needed, handles whiteout/exchange cases, sets redirects or opaque xattrs when moving merge/lower objects, performs upper rename, updates nlink and ctime, and marks modified dirs.
- Tmpfile support uses backing tmpfile open on the upper parent, wraps the real file in `struct ovl_file`, instantiates the overlay dentry, and ensures cleanup if `finish_open()` does not complete.

## State And Data Structures

- Module parameter `redirect_max` bounds absolute redirect xattr length.
- `struct ovl_renamedata` extends VFS `renamedata` with opaque-dir cleanup, nlink update, overwrite, and cleanup-whiteout flags.
- Parent/dentry flags affected include upper alias, revalidation data, opaque, whiteouts, impure, redirect string, and nlink xattrs.
- Uses `OVL_TEMPNAME_SIZE`, whiteout cache state in `struct ovl_fs`, and per-inode overlay nlink state.

## Dependencies

- Depends on overlayfs copy-up, lookup, xattr, ACL, readdir empty-check/whiteout cleanup, inode/nlink helpers, file wrapper allocation, and VFS rename/create/remove wrappers.
- Uses VFS locking helpers such as `start_creating`, `start_removing`, `start_renaming`, `start_renaming_two_dentries`, and scoped credential helpers.
- Uses LSM `security_dentry_create_files_as()` for creation credentials.

## Risks And Invariants

- Upper dentry identity is revalidated under locks before remove/rename to detect stale races.
- Whiteouts and opaque dirs must preserve overlay visibility semantics during atomic replacement.
- Redirect xattrs are required to avoid copying up full directory trees; failure falls back to `-EXDEV`.
- Nested overlay locking order is sensitive around write access, rename locks, and lower/upper inode locks.
- Creation over whiteouts must handle ACLs and umask-mutated modes before making the object visible.
