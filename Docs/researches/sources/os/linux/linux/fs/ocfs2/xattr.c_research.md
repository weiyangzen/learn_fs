# File Research: sources/os/linux/linux/fs/ocfs2/xattr.c

OCFS2 extended attribute implementation. This file owns the full xattr backend for OCFS2: listing, lookup, set/remove, security initialization, ACL/security integration, external value extent management, indexed xattr trees, refcount/reflink handling, journaling, metadata ECC, and VFS xattr handlers.

Primary storage models:
- Inline inode xattrs live at the tail of the inode block after space is carved from inline data, fast symlink payload, or extent-record capacity.
- External unindexed xattrs live in one `ocfs2_xattr_block` referenced by `di->i_xattr_loc`.
- Large xattr sets are stored as an indexed xattr tree rooted in that xattr block; leaf storage is a set of fixed-size xattr buckets.
- Values larger than `OCFS2_XATTR_INLINE_SIZE` are stored outside the name/value area through an embedded `ocfs2_xattr_value_root` extent tree.
- Bucket storage keeps entries sorted by `xe_name_hash`; in-block storage compacts name/value pairs and does not require hash ordering.

Important local abstractions:
- `struct ocfs2_xattr_bucket` wraps the buffer heads that make up one bucket and centralizes bucket read, release, journaling, ECC validation, copying, and dirtying.
- `struct ocfs2_xattr_info` is the normalized set/get request: namespace index, name, value pointer, and value length.
- `struct ocfs2_xattr_search` records the current search result across inode, xattr block, or bucket storage.
- `struct ocfs2_xa_loc` plus `ocfs2_xa_loc_operations` abstracts mutation of inline inode, unindexed block, and indexed bucket entries behind common prepare/store/remove logic.
- `struct ocfs2_xattr_set_ctxt` carries the active transaction, metadata/data allocators, cached deallocations, and abort state.

Lookup and listing:
- `ocfs2_listxattr()` takes the inode cluster lock and `ip_xattr_sem`, lists inline entries first, then external block or indexed tree entries.
- Namespace filtering is done by `ocfs2_xattr_list_entry()`: user xattrs honor `NOUSERXATTR`, POSIX ACL entries require `SB_POSIXACL`, and trusted entries require `CAP_SYS_ADMIN`.
- `ocfs2_xattr_get()` locks the inode and reads under `ip_xattr_sem`; `ocfs2_xattr_get_nolock()` searches inline storage first and falls back to the external xattr block.
- `ocfs2_xattr_find_entry()` validates entry bounds while comparing namespace, name length, and name bytes.
- Indexed lookup hashes the name with the filesystem UUID hash seed, finds the matching extent record, binary-searches buckets by hash range, then linearly scans same-hash entries inside the bucket.

Set/remove flow:
- `ocfs2_xattr_set()` performs VFS flag checks for `XATTR_CREATE` and `XATTR_REPLACE`, prepares refcounted values if needed, flushes the truncate log, reserves metadata/data allocators, starts a journal transaction, and calls `__ocfs2_xattr_set_handle()`.
- `ocfs2_xattr_set_handle()` is the create-inode path used by security/ACL initialization when credits and allocators were already reserved by inode creation.
- New values are attempted in inode-inline xattr space first; if that fails with space pressure, the code falls back to external block or indexed bucket storage.
- If setting succeeds in one storage location while an old copy exists in the other, the old copy is removed in the same logical operation after extending credits.
- Removes truncate external value trees to zero, remove packed entry metadata, update ctime, and may try to remove now-unused refcount trees.
- Mutation updates inode ctime and fsync transaction state.

Name/value mutation details:
- `ocfs2_xa_set()` is the common entry set/remove engine. It journals the backing location, prepares or removes an entry, stores the inline or external value, and dirties the location even on many error paths to keep metadata consistent.
- Block-style storage compacts name/value areas by shifting packed bytes upward on removal and inserting new name/value pairs from the end of the storage area.
- Bucket-style storage can leave holes when a name/value pair cannot be reused; `ocfs2_defrag_xattr_bucket()` later compacts all pairs and restores hash ordering.
- Bucket values must not straddle filesystem block boundaries; helpers align `xh_free_start` before inserting a name/value pair.
- Large-value setup installs a default value root, grows or shrinks the value extent tree, then writes value data block by block under journal access.

External value extent management:
- `ocfs2_xattr_extend_allocation()` adds clusters to an xattr value tree using the normal OCFS2 btree allocator and can extend transactions when data allocation restarts.
- `ocfs2_xattr_shrink_size()` and `__ocfs2_remove_xattr_range()` remove value extents, update `xr_clusters`, drop extent-cache entries, and either decrement refcounts or cache cluster deallocation.
- `__ocfs2_xattr_set_value_outside()` writes the actual large value data into allocated clusters and zero-fills trailing block bytes.
- Cleanup after partial truncate/grow failures intentionally removes corrupt entries or leaks clusters rather than committing inconsistent xattr metadata.

External xattr blocks and indexed trees:
- `ocfs2_create_xattr_block()` allocates and initializes an `ocfs2_xattr_block`, sets signature, block number, suballocator fields, generation, optional indexed root, and links it from the dinode.
- If an unindexed xattr block fills, `ocfs2_xattr_create_index_block()` allocates a bucket cluster, copies/sorts the existing block entries into a bucket, and converts the xattr block body into an indexed tree root.
- `ocfs2_add_new_xattr_bucket()` grows indexed storage by splitting buckets, adding clusters, shifting buckets, or moving bucket ranges across cluster boundaries.
- Bucket splitting preserves the invariant that all entries with the same hash stay in the same bucket; all-same-hash buckets reject further same-hash insertions with `-ENOSPC`.
- Tree traversal walks extent records from high hash to low hash and then iterates buckets in each record.

Refcount and reflink handling:
- Refcounted inodes require special preparation before replacing/removing existing external xattr values.
- `ocfs2_prepare_refcount_xattr()` locks the refcount tree, CoWs existing external xattr value clusters when needed, or computes delete metadata/credits for truncate-driven refcount updates.
- `ocfs2_xattr_attach_refcount_tree()` marks all external xattr value extents refcounted when an inode becomes refcounted.
- `ocfs2_reflink_xattrs()` copies inline xattrs and external xattr blocks/trees from one inode to another, increments refcounts for external value clusters, and can omit security/ACL xattrs when `preserve_security` is false.
- Indexed reflink recreates bucket clusters for the destination and rebuilds xattr tree extents while preserving or recalculating value roots as needed.

Security and namespace handlers:
- Exports `ocfs2_xattr_user_handler`, `ocfs2_xattr_trusted_handler`, and `ocfs2_xattr_security_handler`.
- `ocfs2_init_security_get()` captures LSM-provided security xattrs for create-time sizing or sets them immediately through `security_inode_init_security()`.
- `ocfs2_init_security_set()` installs the captured security xattr through the pre-reserved create path.
- `ocfs2_init_security_and_acl()` reinitializes security and ACL xattrs after reflink when security is not preserved.

Concurrency and journaling invariants:
- `ip_xattr_sem` serializes xattr lookup and mutation.
- `ip_alloc_sem` is used while carving inline xattr space and while converting/growing indexed xattr storage.
- Bucket metadata ECC is validated on read and recomputed before dirtying bucket buffers.
- Mutations must acquire journal access for the exact backing container: dinode, xattr block, bucket, or value data block.
- Truncate-log flushing is coordinated before xattr cluster frees where stale pending deallocations could conflict.
- Refcount tree locks and allocator reservations are ordered before transactions that mutate shared xattr values.

Failure and corruption behavior:
- Bad xattr block signatures, block numbers, fs generations, malformed inline sizes, invalid counts, missing extent records, and bad hash chains are treated as filesystem corruption or I/O errors.
- Many storage-layout BUG_ONs enforce assumptions about bucket size, value locality, block alignment, and extent-tree state.
- Space accounting is conservative and may reserve extra clusters/credits because xattrs can move between inode, block, and indexed tree storage during a set operation.
