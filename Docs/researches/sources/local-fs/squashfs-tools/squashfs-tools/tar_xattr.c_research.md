# File Research: sources/local-fs/squashfs-tools/squashfs-tools/tar_xattr.c

This file imports extended attributes from tar PAX headers into Squashfs xattr lists.

Key functions:
- `read_tar_xattr`: adds one tar xattr to a `tar_file`.
- `read_xattrs_from_tarfile`: returns xattr list/count for an inode backed by a tar entry.
- `free_tar_xattrs`: frees xattr names and the list array.

Important behavior:
- Duplicate xattr names are ignored. This avoids double definitions when archives contain both libarchive and SCHILY encodings for the same xattr.
- Exclude regex is applied first; include regex is applied second.
- `LIBARCHIVE.xattr.*` values are base64-decoded; `SCHILY.xattr.*` values are treated as binary.
- `xattr_get_prefix` maps full names into Squashfs xattr prefix types and fills xattr metadata.

Corruption/edge details:
- Invalid base64 values are logged and ignored.
- Unknown xattr prefixes are logged and ignored, with decoded/copied value storage freed.
- `free_tar_xattrs` frees `full_name` fields and the list container but not `value` fields here, implying value ownership is transferred or handled elsewhere.
