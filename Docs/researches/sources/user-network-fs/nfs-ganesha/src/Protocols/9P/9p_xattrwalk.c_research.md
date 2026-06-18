## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_xattrwalk.c

Purpose: creates a read-only xattr fid either for listing attributes or reading one attribute.

APIs and flow: `_9p_xattrwalk` validates source and attr fids, copies the source fid minus state pointer, initializes op context, allocates xattr buffer, and either lists attributes into a NUL-separated buffer or reads a named xattr, retrying with a larger allocation on `ERANGE`. It stores the attr fid in the connection table, increments object/group/export/credential/parent refs, and returns the xattr size.

State/dependencies: creates persistent attrfid state with read-only cached xattr content. Depends on FSAL list/get xattr operations, fixed list array of 100 entries, and `_9P_XATTR_MAX_SIZE`.

Risks/tests: test list overflow, more than 100 xattrs, large xattr reallocation, `ENOATTR` mapping, attrfid collision, ref balancing on errors, and reading from the attrfid through `_9p_read`.
