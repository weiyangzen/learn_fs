# File Research: sources/os/linux/linux-stable/fs/hfs/attr.c

## Scope

This file exposes classic HFS Finder metadata fields as Linux extended attributes. It supports `hfs.creator` and `hfs.type` for regular data-fork files.

## Public And Internal APIs Covered

- Internal helpers: `__hfs_setxattr()` and `__hfs_getxattr()`.
- VFS handler callbacks: `hfs_xattr_get()` and `hfs_xattr_set()`.
- Handler table: `hfs_xattr_handlers`.

## Control Flow And Behavior

Both get and set reject non-regular files and resource-fork inodes with `-EOPNOTSUPP`. Set initializes a catalog B-tree search, copies the inode catalog key into the search key, finds the matching catalog record, reads a `struct hfs_cat_file`, and updates either `UsrWds.fdType` or `UsrWds.fdCreator` if the supplied value is exactly four bytes. Successful updates write the catalog record back to the B-tree node.

Get returns a size of four when called with size zero. When a buffer is supplied, it performs the same catalog lookup and copies the requested four-byte field if the buffer is large enough, otherwise returns `-ERANGE`.

The public xattr set callback does not support removal: `value == NULL` returns `-EOPNOTSUPP`. Handler flags encode whether the request is for type or creator.

## Dependencies

The file depends on HFS inode private state, catalog B-tree records, `hfs_find_init()`, `hfs_brec_find()`, `hfs_bnode_read()`, `hfs_bnode_write()`, and Linux xattr handler infrastructure.

## Risks And Invariants

The xattr values are fixed-width four-byte Finder fields, not arbitrary strings. The code assumes catalog records found by the inode catalog key are file records of at least `struct hfs_cat_file` size. All B-tree search resources are released with `hfs_find_exit()`.
