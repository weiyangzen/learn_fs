# File Research: sources/os/linux/linux/fs/hfsplus/xattr.c

Purpose: Implements HFS+ extended attribute operations and dispatches xattr namespaces. It manages Finder-info catalog attributes, OS X unprefixed attributes, Linux namespace-prefixed attributes, and lazy creation of the HFS+ Attributes File B-tree.

Key functions:
- `hfsplus_create_attributes_file()` initializes an empty HFS+ Attributes File with header/map nodes, allocates clump blocks, opens the B-tree, and transitions `attr_tree_state`.
- `__hfsplus_setxattr()` handles set/remove requests, special-cases `com.apple.FinderInfo`, creates or replaces inline attributes, and updates catalog xattr/ACL flags.
- `hfsplus_setxattr()` prefixes Linux namespace names before calling the core setter.
- `hfsplus_getxattr_finder_info()` reads Finder info directly from catalog folder/file records.
- `__hfsplus_getxattr()` locates xattr records in the Attributes File and returns inline data; fork/extents xattr payloads are explicitly unsupported.
- `hfsplus_listxattr()` lists Finder info and Attributes File records, converting HFS+ Unicode names and hiding trusted attributes unless privileged.
- `hfsplus_removexattr()` deletes an attribute and clears catalog `HFSPLUS_XATTR_EXISTS`/`HFSPLUS_ACL_EXISTS` flags when appropriate.
- `hfsplus_osx_getxattr()` and `hfsplus_osx_setxattr()` expose OS X unprefixed attributes through the synthetic `osx.` namespace while rejecting known Linux prefixes.

Dependencies and integration:
- Uses HFS+ catalog B-tree lookup, Attributes File B-tree helpers, Unicode conversion helpers, inode dirty marking, and VFS `xattr_handler` registration.
- Coordinates with namespace handlers in `xattr_user.c`, `xattr_trusted.c`, and `xattr_security.c`.
- Uses `HFSPLUS_ATTR_CNID`, catalog flags, and HFS+ inline attribute record structures.

Risk notes:
- Attribute tree creation is stateful and concurrent via `atomic_cmpxchg`; callers can receive `-EAGAIN`, `-EOPNOTSUPP`, `-ENOSPC`, or `-EIO` depending on tree state.
- Only inline attribute data is supported; fork/extents records return `-EOPNOTSUPP`.
- Name buffers are sized for maximum charset expansion, but prefix/name concatenation assumes VFS-provided names fit expected HFS+ limits.
- Finder info does not live in the Attributes File and has separate size validation.
