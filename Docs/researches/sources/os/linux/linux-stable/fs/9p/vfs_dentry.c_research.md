# File Research: sources/os/linux/linux-stable/fs/9p/vfs_dentry.c
- Purpose: Implements 9P dentry lifecycle and validation operations.
- Main functions: `v9fs_cached_dentry_delete`, `v9fs_dentry_release`, `__v9fs_lookup_revalidate`, `v9fs_lookup_revalidate`, dentry unalias lock helpers.
- Dentry release: Walks FIDs stored in `d_fsdata`, removes them, and drops references.
- Revalidation: Refreshes inode attributes when `V9FS_INO_INVALID_ATTR` is set, using dotl or legacy refresh paths based on session protocol.
- Operation tables: Provides cached and uncached dentry operation sets; cached mode adds revalidation and negative-dentry deletion.
- Risks: Dentry aliasing is serialized through the session `rename_sem`; incorrect FID cleanup would leak protocol handles.
