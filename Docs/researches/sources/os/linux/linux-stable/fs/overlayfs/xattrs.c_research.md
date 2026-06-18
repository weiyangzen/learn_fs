# File Research: sources/os/linux/linux-stable/fs/overlayfs/xattrs.c

## Purpose

`xattrs.c` implements overlayfs xattr handlers. It filters overlay-private xattrs from users, supports escaped access to private-looking xattrs, triggers copy-up for xattr mutation, and selects trusted vs user overlay xattr namespaces.

## Main Behavior

Overlayfs private xattrs use either `trusted.overlay.*` or `user.overlay.*` depending on `ofs->config.userxattr`. These are internal metadata and should not normally be exposed as ordinary xattrs.

The file distinguishes:

- Own/private overlay xattrs: current overlay namespace prefix.
- Escaped xattrs: names with an extra `overlay.` escape segment that represent user-visible xattrs whose names would otherwise collide with overlay private metadata.

`ovl_is_private_xattr()` returns true for own overlay xattrs that are not escaped.

## Get/Set Flow

`ovl_xattr_get()` resolves the real backing path for an overlay inode and calls `vfs_getxattr()` under overlay credentials.

`ovl_xattr_set()` selects upper if present or lower otherwise. Removing an xattr from a lower-only object first checks that the xattr exists, then copies up before mutating. All set/remove operations target the upper real dentry and use `ovl_want_write()`/`ovl_drop_write()`. After mutation it calls `ovl_copyattr()` to refresh ctime/mtime and other copied attributes.

## Listing Flow

`ovl_listxattr()` lists real xattrs, then edits the returned list in place:

- Private overlay xattrs are removed.
- Non-trusted xattrs are listed normally.
- Trusted non-overlay xattrs are listed only for `CAP_SYS_ADMIN`.
- Escaped overlay xattrs are unescaped by removing the escape segment from the listed name.

The implementation validates xattr list entry lengths and returns `-EIO` on malformed underlying xattr lists.

## Xattr Handler Sets

The file defines two handler arrays:

- Trusted mode: own trusted overlay handler plus catch-all other handler.
- User mode: own user overlay handler plus catch-all other handler.

`ovl_xattr_handlers(ofs)` returns the active handler set based on `userxattr`.

Own overlay handler get/set operations escape names before delegating, so users can intentionally access xattrs that would otherwise conflict with overlay metadata.

## Dependencies

This file relies on:

- `ovl_i_dentry_upper()`, `ovl_dentry_lower()`, `ovl_i_path_real()`, and `ovl_dentry_real()` from shared overlay state helpers.
- `ovl_copy_up()` to ensure mutations happen on upper.
- `ovl_do_setxattr()`, `ovl_do_removexattr()`, `ovl_want_write()`, and `ovl_copyattr()`.

## Risk Notes

- Incorrect private-xattr filtering can expose or corrupt overlay metadata.
- Copy-up before xattr mutation is required to avoid modifying lower layers.
- Escaping rules must stay consistent with namespace prefix constants in `overlayfs.h`.
