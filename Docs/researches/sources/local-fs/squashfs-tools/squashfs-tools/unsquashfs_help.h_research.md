# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_help.h

Public interface and build-conditional help strings for `unsquashfs_help.c`.

Defines:
- `NOXOPT_STR` and `XOPT_STR`, computed from `XATTR_SUPPORT`, `XATTR_OS_SUPPORT`, and `XATTR_DEFAULT`, to annotate whether `-xattrs` or `-no-xattrs` is default, unsupported, or missing OS support.

Exports:
- Help, section, option, invalid-option, and option-help functions for both `unsquashfs` and `sqfscat`.
- `display_compressors()`.

No state is stored here; it is a declaration/build-policy header.
