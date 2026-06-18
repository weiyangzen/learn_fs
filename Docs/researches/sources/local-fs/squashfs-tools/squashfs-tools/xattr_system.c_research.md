# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xattr_system.c

Mksquashfs-side OS xattr reader.

Primary function:
- `read_xattrs_from_system(dir_ent, filename, xattrs)` lists xattr names with `llistxattr()`, filters them, reads values with `lgetxattr()`, and returns a populated `struct xattr_list` array.

Filtering order:
- Exclude actions from `eval_xattr_exc_actions()`.
- Global exclude regex `xattr_exclude_preg`.
- Include actions from `eval_xattr_inc_actions()`.
- Global include regex `xattr_include_preg`.

Error behavior:
- `ENOTSUP` or no xattrs returns zero silently.
- `ERANGE` on list/value retrieval retries because xattrs may have changed.
- Other list/value failures log and ignore xattrs for that file.
- Unknown Squashfs xattr prefixes are logged and skipped.

Uses `xattr_compat.h` for no-follow API portability.
