# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr.c

## Purpose

Implements HFS+ extended attribute support for Linux VFS xattr handlers, including the special Finder Info pseudo-xattr stored in catalog records and normal xattrs stored in the HFS+ attributes B-tree.

## Main Entry Points

- `hfsplus_xattr_handlers[]`: registers OSX, user, trusted, and security handlers.
- `__hfsplus_setxattr()` / `hfsplus_setxattr()`: set, replace, create, or remove xattrs.
- `__hfsplus_getxattr()` / `hfsplus_getxattr()`: read Finder Info or inline attribute records.
- `hfsplus_listxattr()`: lists Finder Info and attributes B-tree names, applying namespace visibility rules.
- `hfsplus_removexattr()`: deletes B-tree attributes and updates catalog flags.
- `hfsplus_create_attributes_file()`: lazily creates and initializes the attributes B-tree file.

## Control Flow And State

The file rejects xattr operations on resource-fork inodes. Finder Info uses catalog record fields directly and requires exact fixed sizes for file or folder records. Other xattrs require an attributes tree; if missing, set operations try to create one using `attr_tree_state` transitions from empty to creating to valid or failed. B-tree header and map nodes are initialized manually, written page-by-page through the attributes file mapping, and then opened with `hfs_btree_open()`.

For ordinary set operations, catalog lookup runs first, then existing attributes are replaced or new records are created through HFS+ attribute helpers. Catalog flags `HFSPLUS_XATTR_EXISTS` and `HFSPLUS_ACL_EXISTS` are updated after successful writes. Removal deletes the attribute and clears flags if the ACL or final xattr disappears. Reads only support inline data records; fork-data or extents xattrs return `-EOPNOTSUPP`.

Listing first probes Finder Info for nonzero data, then walks the attributes tree from the inode CNID, converts Unicode xattr names to filesystem strings, prefixes unnamespaced names with `osx.`, and hides `trusted.*` unless the caller has `CAP_SYS_ADMIN`.

## Dependencies

Uses HFS+ catalog, attributes, B-tree, inode dirtying, Unicode conversion, Linux xattr namespace constants, and capability checks. It is tightly coupled to `hfsplus_attr_*()` helpers in the attributes implementation.

## Risks

Only inline xattrs are supported for reads. Attribute-tree creation has a state machine that can permanently mark the tree failed for non-ENOSPC errors. Name construction uses fixed maximum HFS+ attribute name sizing. Catalog flag updates and attributes-tree changes must remain consistent or later list/lookup behavior can diverge from on-disk metadata.
