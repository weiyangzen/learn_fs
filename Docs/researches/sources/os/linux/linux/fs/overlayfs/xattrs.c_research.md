# File Research: sources/os/linux/linux/fs/overlayfs/xattrs.c

## Purpose

`xattrs.c` implements overlayfs xattr get/set/list handling. It forwards public xattrs to real backing dentries, copies up lower-only objects before mutation, filters private overlay xattrs from user-visible lists, and supports escaped overlay xattr names so users can store names that would otherwise collide with overlayfs private metadata.

## Main Responsibilities

- Distinguish overlay-private xattrs from user-visible escaped xattrs.
- Forward xattr get operations to the current real backing path.
- Copy up lower-only objects before setting or removing xattrs.
- Require existing lower xattr presence before removing xattrs from lower-only objects.
- Filter private overlay xattrs from `listxattr()`.
- Expose escaped private-prefix xattrs as ordinary names by stripping the escape marker.
- Provide handler sets for `trusted.overlay.*` mode and `user.overlay.*` mode.

## Important Functions

- `ovl_is_escaped_xattr()` detects xattrs using the doubled overlay escape prefix.
- `ovl_is_own_xattr()` detects xattrs in overlayfs' configured private namespace.
- `ovl_is_private_xattr()` returns true for overlay-private metadata xattrs, excluding escaped names.
- `ovl_xattr_get()` selects the real path with `ovl_i_path_real()` and calls `vfs_getxattr()` under overlay credentials.
- `ovl_xattr_set()` copies up if needed, obtains upper write access, and sets or removes the xattr on the upper real dentry.
- `ovl_can_list()` filters private xattrs and restricts trusted xattr visibility to capable callers.
- `ovl_listxattr()` lists real xattrs, removes private overlay names, and unescapes escaped overlay names in place.
- `ovl_xattr_escape_name()` builds an escaped private-prefix xattr name.
- `ovl_own_xattr_get()` and `ovl_own_xattr_set()` access escaped names for overlay-owned prefixes.
- `ovl_other_xattr_get()` and `ovl_other_xattr_set()` pass through all other xattrs.
- `ovl_xattr_handlers()` selects trusted or user handler arrays based on `ofs->config.userxattr`.

## Xattr Escaping Model

Overlayfs reserves `trusted.overlay.*` or `user.overlay.*` for its own metadata. To let users access an xattr with the same apparent prefix, the handler maps it to an escaped name by inserting another `overlay.` segment after the namespace prefix. Listing reverses this by removing `OVL_XATTR_ESCAPE_PREFIX` from escaped entries while hiding true private entries.

## Copy-Up Behavior

When setting an xattr on a lower-only object, overlayfs copies the object up first and then mutates the upper dentry. When removing an xattr from a lower-only object, it first checks whether the lower real xattr exists; if not, the remove fails without copying up. After a successful mutation, overlay inode attributes are refreshed with `ovl_copyattr()`.

## Risk Notes

- Private xattr filtering must exactly match the namespace rules used by `util.c`.
- Escaped-name length can exceed `XATTR_NAME_MAX`, in which case operations return `-EOPNOTSUPP`.
- Removing xattrs from lower-only objects has intentionally different behavior from setting because it avoids unnecessary copy-up if the xattr is absent.
- Trusted xattr listing is gated by `CAP_SYS_ADMIN` in the initial user namespace.
