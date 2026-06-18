# File Research: sources/os/linux/linux-stable/fs/overlayfs/copy_up.c

## Scope

This file implements overlayfs copy-up: copying lower objects into upper/work/index directories, copying data and metadata, handling metacopy, preserving selected xattrs/file attributes/ACLs, setting origin and index file handles, maintaining nlink metadata, using temporary files or workdir temps, and exposing public copy-up entry points.

## Public And Internal APIs Covered

- Public helpers: `ovl_copy_xattr()`, `ovl_set_attr()`, `ovl_encode_real_fh()`, `ovl_get_origin_fh()`, `ovl_set_origin_fh()`, `ovl_maybe_copy_up()`, `ovl_copy_up_with_data()`, `ovl_copy_up()`.
- Copy-up core: `ovl_copy_up_flags()`, `ovl_copy_up_one()`, `ovl_do_copy_up()`, `ovl_copy_up_workdir()`, `ovl_copy_up_tmpfile()`.
- Data/metadata helpers: `ovl_copy_up_file()`, `ovl_copy_up_data()`, `ovl_copy_up_metadata()`, `ovl_copy_up_meta_inode_data()`.
- Index/origin helpers: `ovl_create_index()`, `ovl_set_upper_fh()`, `ovl_link_up()`.
- Credential helpers via scoped cleanup classes for LSM-provided copy-up credentials.
- Module parameter `check_copy_up` is retained as obsolete and always reports `N`.

## Control Flow And Behavior

- Copy-up starts by verifying/lazily locating lower data, then repeatedly copies the topmost ancestor that lacks an upper until the target is copied.
- Metadata-only copy-up is chosen for regular files when metacopy is enabled and the open flags do not require data writes or truncation. Required fs-verity mode forces fallback unless lower data has active verity.
- Data copy-up first tries `vfs_clone_file_range()`. If cloning cannot copy the entire file, it falls back to chunked `do_splice_direct()` with 1 MiB chunks and optional sparse-hole skipping via `SEEK_DATA`.
- Metadata copy-up copies xattrs with LSM filtering, handles POSIX ACLs via ACL APIs, copies selected fileattr flags, stores origin file handles, writes metacopy xattrs and optional fs-verity digest state, restores size/ownership/mode/timestamps, and fsyncs metadata when strict sync policy requires it.
- Workdir copy-up creates a temp object in workdir or indexdir, copies data and metadata, then renames into place under appropriate rename locking.
- O_TMPFILE copy-up writes data/metadata into an unnamed upper tmpfile and links it into the destination.
- Indexed non-directories may be copied directly into the index dir and then hardlinked to the upper dir. Indexed directories are copied to the index area and receive a separate index entry.
- If a dentry already has metacopy metadata but later needs data, `ovl_copy_up_meta_inode_data()` copies lower data into the existing upper file, restores `security.capability` if writing cleared it, removes the metacopy xattr, and marks upper data present.
- Public open-time copy-up skips special files and only acts when open flags require copy-up.

## State And Data Structures

- `struct ovl_copy_up_ctx` carries parent/dentry, lower path, source and parent stats, symlink target, destination dir/name, workdir, origin file handle, origin/index/metacopy flags, digest state, and metadata fsync policy.
- File-handle xattrs use `struct ovl_fh` with magic/version/type/flags/length/uuid and inner exportfs fid.
- Inode flags affected include `OVL_INDEX`, `OVL_HAS_DIGEST`, `OVL_VERIFIED_DIGEST`, and upperdata state.
- Uses overlay xattrs such as origin, upper, metacopy, nlink, and impure markers.

## Dependencies

- Relies on VFS file APIs, exportfs file-handle encoding, splice, clone_file_range, fsync, xattr, ACL, fileattr, fs-verity, LSM copy-up hooks, and scoped credential override helpers.
- Depends heavily on overlayfs helpers from other files for path lookup, temp creation, rename wrappers, xattr wrappers, index naming, metacopy/digest helpers, nlink helpers, lowerdata verification, and inode update.

## Risks And Invariants

- Copy-up must avoid exposing partially initialized upper objects; temp/workdir plus rename/link sequences enforce that.
- Data must be copied before xattrs because writing data can clear `security.capability`.
- Sparse-hole seeking is opportunistic and must fall back to normal copying if unsupported.
- Strict sync policy changes fsync placement to preserve atomic copy-up semantics on filesystems with weak metadata ordering.
- UID/GID must be mappable in the current user namespace before copy-up.
- Copy-up locking deliberately avoids holding upper sb writers across lower llseek in nested overlay cases.
