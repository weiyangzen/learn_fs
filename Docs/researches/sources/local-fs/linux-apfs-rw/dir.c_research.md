# File Research: sources/local-fs/linux-apfs-rw/dir.c

This file implements directory lookup, readdir, create, link, unlink, rmdir, rename, hard-link sibling metadata, and orphan-link handling.

Lookup/readdir:
- `apfs_drec_from_query()` decodes directory records, validates key/value sizes and null-terminated names, extracts optional sibling-id xfields, and maps APFS dentry flags to Linux dirent types.
- `apfs_dentry_lookup()` queries the catalog tree for a child name. For normalization-insensitive volumes it deals with hash collisions by iterating candidates and comparing names.
- `apfs_inode_by_name()` wraps lookup under `nx_big_sem`.
- `apfs_readdir()` emits dots, then queries all matching child records for the directory cnid and emits entries through `dir_emit()`.

Creation:
- Builds hashed or unhashed dentry keys depending on normalization behavior.
- Builds dentry values with date-added, file type, and optional sibling-id xfield.
- `apfs_mkany()` starts a transaction, creates a new inode, creates the inode record, creates dentry/sibling records, optionally stores symlink target xattr, commits, and instantiates the dentry.
- `apfs_mknod`, `apfs_mkdir`, and `apfs_create` are version-adapted wrappers around `apfs_mkany()`.

Hard links:
- Sibling link records list hard-link names for an inode.
- Sibling map records map sibling ids back to file ids.
- When linking the second name to an inode, the original primary dentry may be rewritten to acquire sibling metadata.
- `apfs_link()` increments link count, creates required sibling/dentry records, commits, and instantiates the new dentry.

Deletion/orphans:
- `apfs_delete_dentry()` removes the dentry record and any sibling records, updates parent timestamps and child count, and joins parent inode to the transaction.
- `__apfs_unlink()` drops link count. If it reaches zero, it creates an invisible orphan link under the APFS private directory and decrements volume file counts; otherwise it finds the new primary link.
- `apfs_delete_orphan_link()` removes orphan records during cleanup.
- `apfs_any_orphan_ino()` scans the private directory for regular-file orphan links named `0x<ino>-dead`.

Rename:
- Supports normal rename and `RENAME_NOREPLACE`; rejects unsupported flags such as exchange.
- If replacing a target, unlinks it first.
- Then links the old inode at the new dentry and unlinks the old dentry within one transaction, with undo helpers for abort/commit failure paths.

Research relevance: this file is the APFS catalog mutation layer for namespace operations. It coordinates b-tree records, inode metadata, link counts, private-directory orphan recovery, and Linux VFS API version differences.
