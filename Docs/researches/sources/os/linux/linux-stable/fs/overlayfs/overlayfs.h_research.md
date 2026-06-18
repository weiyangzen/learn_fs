# File Research: sources/os/linux/linux-stable/fs/overlayfs/overlayfs.h

## Purpose

`overlayfs.h` is the central private overlayfs interface. It defines overlay path/xattr/file-handle constants, small VFS wrapper helpers, feature-mode enums, and cross-file function declarations used by overlayfs implementation files.

## Main Contents

- Overlay path-type bits: upper, merge, and origin.
- Overlay private xattr namespace definitions for `trusted.overlay.*` and `user.overlay.*`.
- Overlay xattr IDs such as opaque, redirect, origin, impure, nlink, upper, uuid, metacopy, protattr, and xwhiteout.
- Inode and dentry flag enums for overlay-private state.
- Mount option mode enums for redirect, UUID, xino, verity, and fsync behavior.
- Overlay file-handle wire formats: `struct ovl_fb` and `struct ovl_fh`.
- Metacopy xattr format: `struct ovl_metacopy`.
- Inline wrappers around upper-layer VFS operations with proper mount idmapping.
- Prototypes for utility, lookup, readdir, inode, directory, file, copy-up, export, super, and xattr operations.

## Key Definitions

`struct ovl_fb` is the packed file-handle body stored in xattrs or index names. It includes version, magic, length, flags, fid type, UUID, and a flexible fid array.

`struct ovl_fh` wraps `ovl_fb` with padding so the fid is aligned in memory. Macros such as `OVL_FH_LEN()` and `OVL_FH_FID_OFFSET` describe its in-memory/wire layout.

`struct ovl_metacopy` stores optional fs-verity digest metadata for metadata-only copy-up files. `ovl_metadata_digest_size()` derives digest length from the encoded xattr size.

## VFS Wrapper Helpers

The `ovl_do_*` helpers wrap real upper VFS operations:

- `ovl_do_notify_change()`
- `ovl_do_rmdir()`
- `ovl_do_unlink()`
- `ovl_do_link()`
- `ovl_do_create()`
- `ovl_do_mkdir()`
- `ovl_do_mknod()`
- `ovl_do_symlink()`
- `ovl_do_setxattr()`
- `ovl_do_removexattr()`
- `ovl_do_rename()`
- `ovl_do_whiteout()`
- `ovl_do_tmpfile()`

These consistently use `ovl_upper_mnt_idmap(ofs)` and emit debug traces. This is important for idmapped upper mounts: ownership/mode changes must be interpreted through the upper mount mapping.

## Feature Helpers

Inline helpers encode common feature predicates:

- `ovl_redirect_follow()` and `ovl_redirect_dir()`
- `ovl_origin_uuid()` and `ovl_has_fsid()`
- `ovl_xino_warn()`, `ovl_same_fs()`, `ovl_same_dev()`, `ovl_xino_bits()`
- `ovl_should_sync()`, `ovl_should_sync_metadata()`, `ovl_is_volatile()`
- `ovl_allow_offline_changes()`
- `ovl_force_readonly()`

These are used across lookup, mount setup, copy-up, readdir, export, and sync paths.

## Cross-Module API Surface

This header is the contract between overlayfs compilation units. Notable exported-internal areas:

- `util.c`: stack allocation, path selection, flags, xattrs, whiteouts, metacopy, verity, sync, credential override, and inode attribute copying.
- `namei.c`: file-handle validation, origin/index lookup, lowerdata verification, lookup entry point.
- `readdir.c`: directory operations, merged dir cache, cleanup helpers.
- `inode.c`: permissions, ACLs, inode initialization, fileattr/protattr handling.
- `dir.c`: creation, cleanup, temp names, whiteout cleanup.
- `file.c`: regular file operations and fileattr get/set.
- `copy_up.c`: copy-up and origin encoding.
- `export.c`: export operations.
- `super.c`: `ovl_fill_super()`.
- `xattrs.c`: xattr handlers and overlay get/set/list operations.

## Risk Notes

- This header centralizes subtle idmap and credential semantics; bypassing the wrappers can create ownership or permission bugs.
- File-handle and metacopy layout constants are on-disk/on-wire ABI details.
- The many feature predicates must remain consistent with `params.c` verification and `super.c` fallback behavior.
