# File Research: sources/os/linux/linux-stable/fs/hfsplus/attributes.c

## Scope

Implements HFS+ attributes B-tree key comparison/building and inline extended-attribute create/find/delete/replace operations.

## APIs And Behavior

- `hfsplus_create_attr_tree_cache()` and `hfsplus_destroy_attr_tree_cache()` manage a slab for `hfsplus_attr_entry`.
- `hfsplus_attr_bin_cmp_key()` orders attributes by CNID then attribute Unicode name.
- `hfsplus_attr_build_key()` builds an attribute key from CNID and xattr name using HFS+ Unicode conversion.
- `hfsplus_find_attr()` searches exact attribute names or the first record for a CNID.
- `hfsplus_attr_exists()` probes for an attribute.
- `hfsplus_create_attr()` creates only inline-data attributes, rejecting oversized values with `-E2BIG`.
- `hfsplus_delete_attr()` deletes one inline attribute and rejects fork-data/extents attribute records as unsupported.
- `hfsplus_delete_all_attrs()` repeatedly finds and deletes all attributes for a CNID.
- `hfsplus_replace_attr()` deletes an existing attribute then creates the replacement record.

## State And Dependencies

The file depends on `HFSPLUS_SB(sb)->attr_tree`, B-tree search/mutation, HFS+ name conversion, xattr name type conversion, and inode/tree dirty flags `HFSPLUS_I_ATTR_DIRTY`.

## Risks And Invariants

Linux HFS+ supports Mac OS X style inline xattrs only; fork-data and extents records are recognized but not supported. Delete reads the current key into `fd->search_key` before removal to avoid B-tree corruption from stale cursor data. Replace is not transactional: deletion can succeed and creation can fail.
