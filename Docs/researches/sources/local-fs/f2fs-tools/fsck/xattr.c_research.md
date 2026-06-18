# File Research: sources/local-fs/f2fs-tools/fsck/xattr.c

Implements minimal F2FS extended-attribute read/write support used mainly by sload SELinux labeling.

Key responsibilities:
- `read_all_xattrs()` combines inline xattrs and optional xattr node contents into one temporary buffer, initializes a missing xattr header, and can sanity-check the xattr nid during fsck.
- `__find_xattr()` iterates xattr entries, matches name index/name, and bounds-checks entries against the available xattr space.
- `write_all_xattrs()` copies inline xattr data back into the inode and writes or allocates the external xattr node if the serialized xattr area exceeds inline storage.
- `f2fs_setxattr()` validates name/value length, loads the inode, finds/removes/replaces an entry, checks free space, appends a new entry, writes all xattrs, and updates the inode.
- `inode_set_selinux()` is the exported helper that stores `security.selinux` using F2FS security xattr index.

Important constraints:
- The implementation explicitly asserts that only `F2FS_XATTR_INDEX_SECURITY` is supported in `f2fs_setxattr()`.
- `value == NULL` is rejected early, despite comments describing a remove operation, so this file currently supports set/replace semantics, not removal.
- External xattr blocks are ordinary node blocks with footer space zeroed while reading and preserved/written through node update paths.

Dependencies:
- Uses xattr layout macros from `xattr.h`.
- Uses node allocation/update helpers, NAT lookup, segment entry hints, and `update_block()` for zoned-safe updates.
