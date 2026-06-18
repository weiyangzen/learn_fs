# File Research: sources/os/linux/linux-stable/fs/nfs/dir.c

## Role

`dir.c` implements the Linux NFS client's directory-facing VFS behavior. It wires `nfs_dir_operations` and `nfs_dir_aops`, provides directory open/release/readdir/llseek/fsync, manages NFS dentry revalidation, implements lookup and create-family directory operations, handles unlink/rename with silly-rename protection, and maintains the per-credential NFS ACCESS result cache.

## Main interfaces

- `nfs_dir_operations`: `.iterate_shared = nfs_readdir`, `.open = nfs_opendir`, `.release = nfs_closedir`, `.llseek = nfs_llseek_dir`, `.fsync = nfs_fsync_dir`.
- `nfs_dir_aops`: uses `.free_folio = nfs_readdir_clear_array` so cached directory-entry name allocations are released when page-cache folios go away.
- Exported directory and lookup helpers include `nfs_lookup`, `nfs_atomic_open`, `nfs_atomic_open_v23`, `nfs_create`, `nfs_mknod`, `nfs_mkdir`, `nfs_rmdir`, `nfs_unlink`, `nfs_symlink`, `nfs_link`, `nfs_rename`, `nfs_permission`, `nfs_access_get_cached`, `nfs_access_add_cache`, `nfs_access_zap_cache`, `nfs_set_verifier`, and `nfs_force_lookup_revalidate`.

## Directory stream cache

The file uses a folio-sized directory-entry cache made of `struct nfs_cache_array` and `struct nfs_cache_array_entry`. Each entry stores the server cookie, fileid, name pointer, name length, and d_type. Name strings are copied with `kmemdup_nul()` and intentionally hidden from kmemleak because they are referenced from page-cache memory that kmemleak does not scan.

`nfs_readdir_descriptor` is the central transient state for `nfs_readdir()`: it tracks the file, `dir_context`, current folio, cookie, last cookie, synthetic position, verifier bytes, change/generation attributes, adaptive `dtsize`, whether READDIRPLUS is active, and end-of-buffer/end-of-directory state.

Cookie-to-folio lookup uses `nfs_readdir_folio_cookie_hash()`. Cookie zero maps to index zero, while nonzero cookies are hashed to 18 bits. This lets the page cache hold long cookie-indexed directory streams without growing an enormous XArray.

## READDIR and READDIRPLUS flow

`nfs_readdir()` revalidates the directory mapping, snapshots the open-directory context under `file->f_lock`, decides whether to use READDIRPLUS, then repeatedly searches or fills page-cache folios until the userspace buffer is full or EOF is reached.

Cache lookup starts in `readdir_search_pagecache()` and `find_and_lock_cache_page()`. If a folio needs data, `nfs_readdir_xdr_to_array()` allocates XDR pages, sends `NFS_PROTO(inode)->readdir()`, decodes entries using the protocol-specific `decode_dirent`, and converts decoded entries into one or more `nfs_cache_array` folios. Cookie verifier changes at the beginning of the stream invalidate later cached pages.

READDIRPLUS is selected by `nfs_use_readdirplus()` based on server capability, force mount option, stream start, and recorded cache-hit/cache-miss behavior. When READDIRPLUS returns filehandles and attributes, `nfs_prime_dcache()` opportunistically validates or instantiates child dentries, rejects illegal names, verifies fsid/fileid/filehandle consistency, refreshes inodes, and sets dentry verifiers.

If a cookie cannot be found in the cache, `uncached_readdir()` asks the server for a temporary anonymous stream starting at that cookie. Those folios are not inserted into the page cache because their contents may not be aligned to the page-cache representation and because the ordinary cache should already cover the directory once the scan stabilizes.

## Dentry verifiers and lookup cache consistency

Dentry freshness is driven by parent directory change attributes stored in `dentry->d_time`. Bit 0 is reserved as a delegation tag. `nfs_set_verifier()` stores a verifier only if it still matches the parent; if the parent or child has a read delegation, it marks the verifier as delegated so lookup revalidation can trust it after directory changes until delegation return/revoke paths clear the tag.

`nfs_check_verifier()` compares the saved dentry verifier against the parent directory change attribute and may revalidate the parent inode first. Negative dentries are handled by `nfs_neg_need_reval()`, with stricter behavior for `lookupcache=noneg` and case-insensitive servers.

`nfs_do_lookup_revalidate()` is the common dentry hit path. It handles negative dentries, bad/stale inodes, rename targets on case-insensitive servers, delegated verifiers, close-to-open validation, LOOKUP_RCU limitations, and fallback wire lookups through `nfs_lookup_revalidate_dentry()`.

For NFSv4, `nfs4_lookup_revalidate()` optimizes regular-file `LOOKUP_OPEN` so later file open code can perform the real OPEN/revalidation, while still falling back to full dentry revalidation for directories, mountpoints, negative dentries, non-regular files, exclusive/revalidation flags, or changed parent directories.

## Lookup, open, create, and namespace mutation

`nfs_lookup()` validates name length, skips ordinary lookup for exclusive create and rename target intents, performs protocol lookup, creates or finds the inode with `nfs_fhget()`, sets the dentry verifier, and uses `d_splice_alias()`.

`nfs_atomic_open()` implements NFSv4 atomic OPEN integration. It validates flags, prepares mode/truncation attributes, handles negative dentry replacement for non-create opens, creates an NFS open context, calls `NFS_PROTO(dir)->open_context()`, marks `FMODE_CREATED` when the server creates the file, and finishes only regular files. Errors such as `-EISDIR`, `-ENOTDIR`, and follow-related `-ELOOP` fall back to lookup/no-open handling.

`nfs_atomic_open_v23()` provides NFSv2/v3 create-plus-open behavior with different truncation handling. It tries `nfs_do_create()` for `O_CREAT`, returns a finished open on success, and otherwise falls back to lookup unless exclusive-create semantics require the error.

Create-like operations (`nfs_create`, `nfs_mknod`, `nfs_mkdir`, `nfs_symlink`) call protocol-specific RPC operations, drop dentries on ambiguous failed create/mknod/symlink paths, and set dentry verifiers on success. `nfs_symlink()` builds a raw folio containing the symlink target, sends it to the server, and opportunistically inserts that folio into the new inode mapping.

`nfs_link()` drops the target dentry, syncs regular-file data first, sends LINK, and instantiates the target dentry on success. `nfs_rmdir()` serializes with the child inode's `rmdir_sem`, clears link count on successful server removal, and updates verifier/negative dentry state for `-ENOENT`.

`nfs_unlink()` chooses silly rename when the dentry has extra users and the inode is not marked preserve-unlinked. Otherwise it blocks lookup revalidation via `d_fsdata = NFS_FSDATA_BLOCKED`, performs `nfs_safe_remove()`, updates verifier/error state, then wakes waiters.

`nfs_rename()` rejects nonzero VFS flags, silly-renames a busy non-directory target if necessary, blocks revalidation for direct target replacement, syncs old regular-file data for unsafe rename cases, executes `nfs_async_rename()` and waits for completion, invalidates old inode attributes on success, moves the dentry locally under VFS locks, and drops target link count when overwriting.

## ACCESS cache and permissions

The file maintains a global LRU and per-inode red-black tree of `nfs_access_entry` objects keyed by fsuid, fsgid, and group list. `nfs_access_get_cached()` first attempts a lockless RCU lookup of the most-recent entry, then falls back to locked RB-tree search. Entries are invalidated when inode access cache state is stale, when user login time is newer than the entry timestamp, or when explicit zap/shrinker paths run.

`nfs_access_add_cache()` copies credential identity and the ACCESS mask into a new entry, inserts or replaces it in the RB tree, links it into per-inode and global LRUs, updates `nfs_access_nr_entries`, and enforces `nfs_access_max_cachesize`.

`nfs_access_cache_scan()` and `nfs_access_cache_count()` are shrinker callbacks registered elsewhere. The scan walks the global inode LRU, evicts one entry per inode visit, and clears the inode LRU flag when the per-inode list becomes empty.

`nfs_permission()` avoids unnecessary ACCESS RPCs for symlinks, NFSv4 atomic-open regular-file opens, and pure directory writes that the server will check during the operation. Otherwise it calls `nfs_do_access()`, which fetches or sends an ACCESS RPC and converts NFS access bits to Linux `MAY_*` bits. Execute checks additionally revalidate mode if needed and call `execute_ok()`.

## Concurrency and failure behavior

Directory-open state is held in `nfs_open_dir_context` and linked on the inode under `i_lock`, with RCU deletion on close. Dentry blocking for unlink/rename uses `wait_var_event()` and release-store wakeups on `d_fsdata`. Directory folio cache entries are locked through the page cache during fill/search. Access-cache updates use inode locks, a global LRU spinlock, RCU freeing, and explicit memory barriers around global accounting/list visibility.

The code treats `-EBADCOOKIE` and `-ENOTSYNC` as signals to invalidate or bypass directory cache state. `-ENOTSUPP` on READDIRPLUS disables server READDIRPLUS capability for this mount. Soft revalidation can accept cached roots after timeout, while stale non-root entries are dropped or marked for revalidation.
