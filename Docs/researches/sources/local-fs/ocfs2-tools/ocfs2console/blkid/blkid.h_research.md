# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/blkid.h

`blkid.h` is the public interface for the vendored legacy libblkid copy. It defines opaque device/cache/iterator types, version/date constants, device lookup flags, and prototypes for cache management, device iteration, probing, resolving tag values, tag iteration, tag parsing, and version parsing.

The header uses LGPL terms, C++ guards, and `blkid_types.h` for fixed-width blkid types. It mirrors early e2fsprogs/libblkid API shape so `ocfs2console` can build without a system blkid.
