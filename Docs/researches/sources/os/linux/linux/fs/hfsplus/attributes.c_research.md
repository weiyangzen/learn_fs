# File Research: sources/os/linux/linux/fs/hfsplus/attributes.c

Purpose: Implements HFS+ attributes B-tree support for extended attributes, limited to inline data records.

Key functions:
- `hfsplus_create_attr_tree_cache()` and `hfsplus_destroy_attr_tree_cache()` manage a kmem cache for attribute entries.
- `hfsplus_attr_bin_cmp_key()` sorts attribute keys by CNID and Unicode attribute name.
- `hfsplus_attr_build_key()` converts xattr names to HFS+ Unicode attribute keys.
- `hfsplus_attr_build_record()` creates inline/fork/extents records, but only inline data is meaningfully supported.
- `hfsplus_find_attr()` searches by full key or first record by CNID.
- `hfsplus_attr_exists()` checks whether an attribute exists.
- `hfsplus_create_attr()`, `hfsplus_delete_attr()`, `hfsplus_delete_all_attrs()`, and `hfsplus_replace_attr()` mutate the attributes tree and mark relevant inodes dirty.

Dependencies and integration:
- Uses generic HFS+ B-tree find/record mutation APIs.
- Called by HFS+ xattr handlers and catalog deletion cleanup.
- Marks both the attributes tree inode and owning inode with `HFSPLUS_I_ATTR_DIRTY`.

Risk notes:
- Fork-data and extents attributes return unsupported behavior; Linux HFS+ only stores inline xattr data here.
- `hfsplus_delete_all_attrs()` repeatedly searches first-by-CNID after each deletion, relying on B-tree ordering and mutation stability.
