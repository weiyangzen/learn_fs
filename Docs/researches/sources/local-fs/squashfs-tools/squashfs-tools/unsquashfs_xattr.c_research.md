# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_xattr.c

Unsquashfs-side xattr helpers that are independent of OS xattr writing.

Key functions:
- `has_xattrs()` checks both inode xattr index validity and whether the filesystem has an xattr table.
- `print_xattr_name_value()` emits pseudo-file xattr assignments, preserving printable values directly and encoding non-printable/backslash bytes using `0t` octal escapes.
- `print_xattr()` loads an xattr id with `get_xattr()`, validates bounds, applies exclude/include regex filters, and writes pseudo xattr records as `<pathname> x <name>=<value>`.
- `xattr_regex()` compiles extended regexes for include/exclude options and reports invalid patterns fatally.

Dependencies:
- `read_xattrs.c` APIs declared in `xattr.h` for loading/freeing xattr lists.
- Global `sBlk`, strict-error policy, and output write helpers from `unsquashfs`.
