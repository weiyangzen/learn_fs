# File Research: sources/os/linux/linux-stable/fs/fuse/dir.c

## Purpose

`dir.c` implements FUSE VFS directory, dentry, inode operation, permission, lookup, symlink, getattr/statx, and setattr behavior. It translates Linux VFS operations into FUSE protocol requests while maintaining kernel-side dentry and attribute caches with server-provided timeouts.

## Main Responsibilities

- Maintains FUSE dentry private data, dentry validity timeouts, stale-entry invalidation, and optional periodic stale dentry cleanup.
- Implements lookup and dentry revalidation using `FUSE_LOOKUP`, including negative dentries, epoch invalidation, readdirplus hints, and automount submount entries.
- Implements directory and namespace mutations: create, tmpfile, mknod, mkdir, symlink, unlink, rmdir, rename, and link.
- Adds creation extensions for security context (`FUSE_SECURITY_CTX`) and supplementary parent-group information (`FUSE_CREATE_SUPP_GROUP`).
- Implements attribute retrieval through `FUSE_GETATTR` and optional `FUSE_STATX`, with local cache fallback when attributes remain valid.
- Implements permission checks for both kernel-side `default_permissions` mode and server-side `FUSE_ACCESS` mode.
- Implements symlink readlink caching/non-caching paths.
- Implements directory open/release/fsync/ioctl wrappers.
- Implements `SETATTR`, including truncate, open(O_TRUNC), writeback-cache time handling, killpriv, DAX layout breakage, and writepage exclusion.
- Installs FUSE inode/file operation tables for directories, common inodes, and symlinks.

## Dentry and Attribute Cache Model

FUSE maintains separate timeout state for dentries and inode attributes:
- Dentry timeout lives in `struct fuse_dentry`.
- Attribute timeout lives in `fuse_inode->i_time`.
- `fuse_time_to_jiffies()` converts protocol timeout fields to jiffies.
- `fuse_change_entry_timeout()` updates dentry validity after lookup/create replies.
- `fuse_invalidate_attr_mask()` marks selected statx fields stale.
- `fuse_invalidate_entry_cache()` marks a dentry stale without necessarily removing it.

The optional `inval_wq` module parameter enables a delayed workqueue that keeps an rb-tree of expiring dentries and disposes unused expired entries. `delete_stale` also toggles `DCACHE_OP_DELETE` so stale dentries are dropped more aggressively.

## Lookup and Revalidation

`fuse_dentry_revalidate()` is central:
- Rejects dentries older than the connection epoch.
- Rejects bad inodes.
- Refreshes expired positive dentries with `FUSE_LOOKUP`.
- Treats zero nodeid as `-ENOENT`.
- Detects nodeid/type/submount mismatches and asks VFS to invalidate.
- Refreshes inode attributes and dentry timeout when the same inode is confirmed.
- Uses `FUSE_I_INIT_RDPLUS` and `FUSE_I_ADVISE_RDPLUS` to adaptively encourage readdirplus after lookup/readdir interaction.

`fuse_lookup_name()` sends raw lookups and creates inodes with `fuse_iget()`. `fuse_lookup()` wraps it for VFS, handles negative results, prevents root aliases, splices aliases, and records the current connection epoch in `dentry->d_time`.

## Create and Namespace Operations

Creation helpers share common reply handling through `create_new_entry()`:
- Allocates a forget request before sending the operation.
- Sends operation-specific protocol input.
- Adds creation extension arguments when negotiated.
- Validates nodeid, file type, and attributes.
- Instantiates or splices the returned inode.
- Updates parent directory attributes/version.

`fuse_create_open()` implements atomic create/open for `FUSE_CREATE` and `FUSE_TMPFILE`, allocating `struct fuse_file`, saving the open reply, instantiating the inode, and completing `finish_open()`. If the server lacks create support, `fuse_atomic_open()` falls back to mknod plus normal open.

Mutations invalidate or refresh local cache state carefully:
- `unlink`/`rmdir` update parent directory state, reduce link counts, invalidate entry cache, and invalidate ctime.
- `rename` updates ctime for moved entries, invalidates on interrupted/unknown outcomes, and supports `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT` when `FUSE_RENAME2` is available.
- `link` uses `FUSE_LINK`, falling back to `-EPERM` after `-ENOSYS`.

## Attributes, Statx, and Permission

`fuse_update_get_attr()` decides whether to call the server:
- Honors `AT_STATX_FORCE_SYNC` and `AT_STATX_DONT_SYNC`.
- Requests only FUSE-supported fields: basic stats and optionally btime.
- Uses `FUSE_STATX` when btime is requested and the server supports it.
- Falls back to cached `generic_fillattr()` and preserved FUSE fields when valid.

`fuse_permission()` enforces the FUSE access model:
- First checks `fuse_allow_current_process()` to prevent unauthorized callers from entering a user-controlled filesystem.
- In `default_permissions` mode, refreshes mode/uid/gid if stale and calls `generic_permission()`.
- In remote-check mode, sends `FUSE_ACCESS` for access/chdir checks.
- Always keeps local execute checks for regular files.

## Setattr and Truncation

`fuse_do_setattr()` is the main setattr implementation:
- Uses `setattr_prepare()`, with `ATTR_FORCE` when the server handles permissions.
- Converts VFS `iattr` into `fuse_setattr_in`, including idmapped uid/gid translation.
- Handles `ATTR_OPEN` with `atomic_o_trunc` as a local page-cache truncate.
- Blocks writepages during truncate with `FUSE_NOWRITE`.
- Marks size unstable with `FUSE_I_SIZE_UNSTABLE`.
- Breaks DAX layouts before truncating DAX inodes.
- Sends file-handle based setattr when available.
- Adds kill-suid/sgid flags for truncate/chown when `handle_killpriv_v2` is negotiated.
- Updates local inode attributes and page cache only after a successful server reply.

This path is sensitive because writeback-cache mode trusts local size/mtime/ctime more than server replies.

## Operation Tables

The file installs:
- `fuse_dir_inode_operations` for directories.
- `fuse_dir_operations` for directory files.
- `fuse_common_inode_operations` for regular and special inode metadata operations.
- `fuse_symlink_inode_operations` and `fuse_symlink_aops` for symlinks.

## Edge Cases and Risks

- Interrupted namespace operations may have completed in userspace, so the kernel invalidates affected dentries but cannot fully repair all race cases.
- Attribute cache invalidation must be field-specific because writeback cache keeps local size/time authoritative.
- `SETATTR` truncate paths coordinate inode locks, page-cache invalidation, writeback exclusion, and DAX layout breaking.
- Permission checks intentionally avoid entering the userspace server for callers the mounter could not ptrace.
