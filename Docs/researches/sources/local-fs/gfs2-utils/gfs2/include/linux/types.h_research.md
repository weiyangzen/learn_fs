# File Research: sources/local-fs/gfs2-utils/gfs2/include/linux/types.h

This header supplies userspace definitions needed by `gfs2_ondisk.h` for Linux-style integer and endian-annotated types.

It includes `<asm/types.h>` and `<stdint.h>`, defines sparse-style `__bitwise` and `__force` annotations when `__CHECKER__` is active, and typedefs:
- `__le16`, `__be16`
- `__le32`, `__be32`
- `__le64`, `__be64`

The file is a compatibility shim so userspace gfs2-utils code can share kernel-like on-disk structure declarations without depending directly on the full kernel header environment.
