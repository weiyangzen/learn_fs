# File Research: sources/os/linux/linux/fs/overlayfs/overlayfs.h

## Purpose

`overlayfs.h` is the central private overlayfs header. It defines overlay path-type bits, xattr namespace constants, on-disk metadata formats, feature-mode enums, idmapped upper-layer VFS wrappers, and cross-file function declarations for the overlayfs implementation.

## Main Contents

- Overlay path type bits: upper, merge, and origin.
- Private xattr namespace definitions for `trusted.overlay.*`, `user.overlay.*`, and escaped overlay xattrs.
- Overlay xattr IDs for opaque, redirect, origin, impure, nlink, upper, uuid, metacopy, protattr, and xwhiteout.
- Overlay inode and dentry flag enums.
- Mount option mode enums for redirect, UUID, xino, verity, and fsync behavior.
- File-handle ABI structures `struct ovl_fb` and `struct ovl_fh`.
- Metacopy xattr ABI structure `struct ovl_metacopy`.
- Inline wrappers around upper-layer VFS operations.
- Prototypes for util, lookup, readdir, inode, dir, file, copy-up, export, super, and xattr modules.

## Key Definitions

`struct ovl_fb` is the packed file-handle body stored in xattrs and encoded index names. It includes version, magic, length, flags, fid type, filesystem UUID, and the flexible file identifier array.

`struct ovl_fh` wraps `struct ovl_fb` with padding so the fid area is 32-bit aligned in memory. `OVL_FH_WIRE_OFFSET`, `OVL_FH_LEN()`, and `OVL_FH_FID_OFFSET` describe the in-memory and wire layout.

`struct ovl_metacopy` stores optional fs-verity digest metadata for metadata-only copy-up files. `OVL_METACOPY_MIN_SIZE`, `OVL_METACOPY_MAX_SIZE`, and `ovl_metadata_digest_size()` define its ABI sizing rules.

## VFS Wrapper Helpers

The `ovl_do_*` inline helpers route upper-layer operations through the upper mount idmap and emit debug tracing. They cover:

- metadata changes: `ovl_do_notify_change()`
- directory and file creation/removal: `ovl_do_create()`, `ovl_do_mkdir()`, `ovl_do_mknod()`, `ovl_do_symlink()`, `ovl_do_rmdir()`, `ovl_do_unlink()`
- linking and renaming: `ovl_do_link()`, `ovl_do_rename()`, `ovl_do_rename_rd()`
- xattrs and ACLs: `ovl_do_getxattr()`, `ovl_do_setxattr()`, `ovl_do_removexattr()`, `ovl_do_set_acl()`, `ovl_do_remove_acl()`
- whiteouts and temporary files: `ovl_do_whiteout()`, `ovl_do_tmpfile()`
- upper lookup/create/remove helpers: `ovl_lookup_upper_unlocked()`, `ovl_start_creating_upper()`, `ovl_start_removing_upper()`

The idmap usage is important: upper-layer ownership and mode changes must be interpreted through the upper mount mapping, not the overlay mount.

## Feature Helpers

Inline predicates encode common feature decisions:

- `ovl_redirect_follow()` and `ovl_redirect_dir()`
- `ovl_origin_uuid()` and `ovl_has_fsid()`
- `ovl_xino_warn()`, `ovl_same_fs()`, `ovl_same_dev()`, `ovl_xino_bits()`
- `ovl_should_sync()`, `ovl_should_sync_metadata()`, `ovl_is_volatile()`
- `ovl_allow_offline_changes()`
- `ovl_force_readonly()`

These helpers keep feature checks consistent across lookup, copy-up, readdir, export, mount setup, and sync paths.

## Cross-Module API Surface

The header exposes overlayfs-internal APIs from:

- `util.c`: credential override, write accounting, stack allocation, path resolution, dentry flags, xattrs, copy-up synchronization, metacopy, verity, volatile sync, and attribute copying.
- `namei.c`: file-handle validation, origin/index lookup, lowerdata verification, and lookup operations.
- `readdir.c`: directory operations, merged cache handling, whiteout cleanup, d_type checks, and index/workdir cleanup.
- `inode.c`: permissions, ACLs, inode initialization, nlink accounting, fileattr/protattr support, trap inodes, and attribute updates.
- `dir.c`: create/remove/rename support, temp names, whiteouts, and cleanup.
- `file.c`: regular file operations and fileattr access.
- `copy_up.c`: copy-up flow, xattr copying, origin encoding, and upper attribute setup.
- `export.c`: export operations.
- `super.c`: `ovl_fill_super()`.
- `xattrs.c`: overlay xattr handlers and public xattr operations.

## Risk Notes

- The file-handle and metacopy structures are persistent ABI details; layout changes must preserve compatibility.
- Upper VFS wrapper bypasses can create idmapped mount bugs or permission inconsistencies.
- Private xattr namespace rules must match `xattrs.c` filtering and escaping.
- Feature predicates must stay aligned with `params.c` verification and `super.c` fallback behavior.
