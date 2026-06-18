# File Research: sources/os/linux/linux/fs/afs/dir.c

Purpose: implements AFS directory file/inode/dentry operations, complete remote directory reads, directory iteration, lookup and bulk-status lookup-ahead, dentry revalidation, create/remove/link/symlink/rename operations, local directory-cache edits after server mutations, and directory cache writeback.

Key interfaces:
- `afs_dir_file_operations`, `afs_dir_inode_operations`, `afs_dir_aops`, `afs_fs_dentry_operations`.
- Directory read/iterate: `afs_read_dir()`, `afs_dir_iterate()`, `afs_readdir()`.
- Lookup/revalidation: `afs_lookup()`, `afs_d_revalidate()`, `afs_d_delete()`, `afs_d_iput()`.
- Mutations: create, mkdir, rmdir, unlink, link, symlink, rename.
- `afs_dir_writepages()` writes directory folio-queue contents to cache as one blob.

Implementation notes:
- AFS directories are read synchronously as a single unit with `netfs_read_single()` to avoid observing inconsistent directory contents across multiple reads.
- Directory storage is a folio queue in the vnode; valid/read state is tracked by `AFS_VNODE_DIR_VALID` and `AFS_VNODE_DIR_READ`.
- Directory blocks are 2048-byte AFS XDR blocks; validation checks magic, forces final byte NUL, and dumps the directory on failure.
- Iteration walks bitmap-marked slots, validates multi-slot names, computes the next slot by name length, and emits vnode number plus unique ID for internal lookup filldir paths.
- Lookup first validates the parent, handles `@sys` substitution through configured sysnames, hashes/searches the directory, then optionally scans ahead for up to 50 FIDs and uses FS/YFS InlineBulkStatus for speculative inode population.
- Dentry versions are stored in `d_fsdata` using directory data version. Revalidation compares against current `data_version` and `invalid_before`; slow revalidation can re-search by name and compare vnode/unique.
- Dentries for deleted, silly-renamed, or pseudodir inodes are unhashed.
- Mutating operations allocate `afs_operation`, set vnode parameters and expected data-version deltas, issue FS/YFS RPCs, commit statuses, and edit the local directory cache only if the server data-version delta matches exactly.
- Unlink and rename integrate sillyrename for busy files, using `DCACHE_NFSFS_RENAMED`.
- Rename handles normal, YFS no-replace, and YFS exchange paths; updates child `..` entries and directory data versions for moved subdirectories.
- Directory writeback locks `validate_lock` and writes the folio queue through netfs only if the directory cache is valid.

Dependencies:
- Netfs/fscache, AFS operation framework, fsclient/yfsclient RPCs, callback validation, directory edit/search helpers, sillyrename helpers, sysname substitution, dentry and inode versioning.

Edge cases:
- Directory read retries on `-ESTALE`, with retry limits.
- Very small or over-large directories are rejected.
- RCU revalidation returns `-ECHILD` when it cannot prove validity.
- Rename intentionally drops dentries around server operations to avoid races with `d_revalidate()` seeing stale parent data versions.
