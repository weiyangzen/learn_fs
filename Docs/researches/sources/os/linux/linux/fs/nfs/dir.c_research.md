# File Research: sources/os/linux/linux/fs/nfs/dir.c

## Role

`dir.c` is the NFS client’s directory and name-resolution implementation. It supplies directory file operations, dentry operations, VFS inode operations for namespace mutations, readdir caching, lookup revalidation, access permission caching, and NFS-specific unlink/rename behavior.

Major exported surfaces include `nfs_dir_operations`, `nfs_dir_aops`, `nfs_dentry_operations`, `nfs4_dentry_operations`, `nfs_lookup`, `nfs_atomic_open`, `nfs_atomic_open_v23`, `nfs_create`, `nfs_mknod`, `nfs_mkdir`, `nfs_rmdir`, `nfs_unlink`, `nfs_symlink`, `nfs_link`, `nfs_rename`, `nfs_access_get_cached`, `nfs_access_add_cache`, `nfs_may_open`, and `nfs_permission`.

## Directory Reading And Cache Model

The file implements a custom readdir cache stored in folios via `struct nfs_cache_array`. Each array stores directory cookies, inode numbers, names, d_type, a change attribute, EOF/full flags, and an ordered-cookie hint. Names are copied with `nfs_readdir_copy_name()` and released by `nfs_readdir_clear_array()` through `nfs_dir_aops.free_folio`.

`nfs_readdir()` is the central path. It creates a `struct nfs_readdir_descriptor`, revalidates the mapping, chooses READDIRPLUS via `nfs_use_readdirplus()`, searches or fills cached folios, emits entries with `nfs_do_filldir()`, and stores cursor state back in `struct nfs_open_dir_context`.

The cache is indexed by `nfs_readdir_folio_cookie_hash()`, which hashes NFS cookies into page-cache indexes with a bounded 18-bit hash space. Cookie and position handling differs for 32-bit APIs through `nfs_readdir_use_cookie()`, falling back to positional offsets when full cookies cannot be safely represented.

When cached cookie lookup fails, `uncached_readdir()` asks the server starting at the problematic cookie and emits temporary folios without inserting them into the page cache. This handles deleted entries or server cookie loss without corrupting the primary directory cache.

## READDIRPLUS And Dcache Priming

`nfs_readdir_entry_decode()` uses `xdr_decode()` and, for READDIRPLUS, calls `nfs_prime_dcache()` to populate or refresh child dentries from returned filehandles and attributes. `nfs_prime_dcache()` validates names, rejects `.`/`..`, embedded NUL and `/`, compares fsid/fileid/filehandle, refreshes matching inodes, invalidates stale mismatches, and uses `d_alloc_parallel()`/`d_splice_alias()` for concurrent lookup-safe insertion.

The file tracks lookup cache hits and misses per open directory. `nfs_readdir_record_entry_cache_hit()` and `nfs_readdir_record_entry_cache_miss()` feed the heuristic in `nfs_use_readdirplus()`. `nfs_lookup_advise_force_readdirplus()` nudges future readdir calls when ordinary lookup indicates READDIRPLUS may help.

## Dentry Revalidation

The dentry verifier is based on the parent directory change attribute stored in `dentry->d_time`. `nfs_force_lookup_revalidate()` advances the directory cache-change attribute. `nfs_set_verifier()` records a verifier and tags it when a directory or file read delegation allows trusted revalidation.

`nfs_lookup_revalidate()` and `nfs4_lookup_revalidate()` drive dcache validation. They handle negative dentries, RCU pathwalk constraints, close-to-open checks, `LOOKUP_REVAL`, `LOOKUP_OPEN`, atomic-open shortcuts, delegated dentries, case-insensitive server behavior, and stale inode detection. Full validation goes through `NFS_PROTO(dir)->lookup()` and compares returned filehandles with the cached inode.

`block_revalidate()` and `unblock_revalidate()` use `dentry->d_fsdata == NFS_FSDATA_BLOCKED` to pause lookup/open races during unlink or overwrite rename.

## Namespace Operations

`nfs_lookup()` performs ordinary lookup unless skipped for exclusive create or rename target. It allocates fhandle/fattr, performs protocol lookup, handles negative dentries including case-insensitive verifier handling, creates/obtains an inode via `nfs_fhget()`, and splices aliases.

`nfs_atomic_open()` handles NFSv4-style open-context based atomic open, including create/truncate attributes, O_DIRECTORY fallback, regular-file enforcement, and `FMODE_CAN_ODIRECT`. `nfs_atomic_open_v23()` implements the NFSv2/v3 create-plus-lookup/open path.

Creation helpers include `nfs_do_create()`, `nfs_create()`, `nfs_mknod()`, `nfs_mkdir()`, and `nfs_instantiate()`. Failed creates and mknods drop dentries because a server-side success may have been hidden by reply-path errors.

Removal and rename logic is NFS-specific:
- `nfs_rmdir()` serializes positive directory removal with `rmdir_sem` and clears link count on success.
- `nfs_unlink()` performs sillyrename when the dentry has active references, otherwise blocks revalidation and calls `nfs_safe_remove()`.
- `nfs_safe_remove()` invalidates link state and calls protocol `remove`.
- `nfs_rename()` handles busy overwrite targets with sillyrename, blocks target revalidation when needed, may sync regular files for unsafe cross-directory renames, waits for async RPC completion, invalidates old inode attributes, moves dentries locally, and drops replaced target link state.

`nfs_symlink()` allocates a folio containing the link body, sends the SYMLINK RPC, then opportunistically inserts the folio into the new inode mapping. `nfs_link()` syncs regular files before hardlink RPC and installs the target dentry on success.

## Access Permission Cache

The file maintains a global LRU and per-inode rb-tree of `struct nfs_access_entry` keyed by fsuid, fsgid, and supplementary groups. `nfs_access_get_cached()` first tries an RCU fast path for the most recent entry, then a locked rb-tree lookup. Entries are invalidated on `NFS_INO_INVALID_ACCESS` and also checked against login time to avoid reusing credentials across changed login sessions.

`nfs_access_add_cache()` copies credential identity and returned access mask, inserts/replaces in the rb-tree, updates LRU/accounting, and enforces `nfs_access_max_cachesize`. The shrinker hooks `nfs_access_cache_scan()` and `nfs_access_cache_count()` reclaim entries under memory pressure.

`nfs_permission()` maps VFS permission checks onto NFS ACCESS RPCs when available. It avoids unnecessary checks for symlinks, directory write-only operations, and atomic-open regular-file opens. It falls back to inode revalidation plus `generic_permission()` if ACCESS is unsupported.
