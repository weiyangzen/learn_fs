# File Research: sources/local-fs/xfsprogs/libxfs/listxattr.h

Header for libxfs xattr walking.

Key responsibilities:
- Defines `xattr_walk_fn` callback signature.
- Declares `xattr_walk`.

Dependencies:
- Used by `db/rdump.c` and any other userspace code needing attr enumeration.

Notable risks:
- Callback receives optional value pointer; remote attrs provide length without inline value data.
