# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_acl.c

This file implements UFS POSIX-draft ACL storage, access checks, inheritance, and ACL cache management. UFS stores nontrivial ACLs in special shadow inodes, while ordinary owner/group/other ACLs are collapsed back into mode bits with no shadow inode.

The central storage routine is `ufs_si_store`. Given an in-core `si_t`, it either removes ACL storage when only the three basic access entries remain, reuses an identical cached shadow inode, or allocates a new `IFSHAD` inode and writes serialized ACL data into it. When switching an object to the new ACL, it updates `i_ufs_acl`, `i_shadow`, mode bits, owner/group fields implied by ACL entries, and inode transaction state. It then decrements the old shadow inode link count and old ACL reference count, deleting the cache entry if no in-memory inode references remain.

`ufs_si_load` attaches an inode's existing shadow ACL. It validates `i_shadow`, looks up a cached `si_t` by device and shadow inode number, or reads the shadow inode from disk, parses `FSD_ACL` and `FSD_DFACL` records into `vsecattr_t`, sorts and validates them, converts them into an in-core `si_t`, and inserts the result into both ACL caches. Internal inconsistencies mark the shadow inode `ISTALE` so stray damaged shadow inodes are not kept alive.

`ufs_acl_access` implements the POSIX ACL access algorithm: owner entry first, then matching `ACL_USER`, then owning group and matching `ACL_GROUP` entries under the ACL mask, and finally `OTHER_OBJ`. Privilege fallback is delegated through `MODE_CHECK`.

`ufs_acl_get` returns either the stored ACL via `aclentry2vsecattr` or fabricates a four-entry ACL from mode bits (`USER_OBJ`, `GROUP_OBJ`, `OTHER_OBJ`, `CLASS_OBJ`) when no shadow ACL exists. `ufs_acl_set` requires owner or privilege, converts caller-provided `vsecattr_t` to `si_t`, normalizes owner and group object IDs to the inode UID/GID, and stores it through `ufs_si_store`.

The conversion and validation layer includes `acl_validate`, `vsecattr2aclentry`, `aclentry2vsecattr`, `formacl`, `formvsec`, `ufs_sectobuf`, and ACL list copy/free helpers. Validation rejects duplicate entries, unknown types, bad permissions, missing required regular ACL owner/group/other entries, group entries without masks, malformed default ACL triples, and lists exceeding `MAX_ACL_ENTRIES`.

`ufs_si_inherit` constructs inherited ACLs from a parent directory's default ACL. It requires a complete default owner/group/other triple, copies default entries into the child's access ACL, applies creation mode to owner/group/other entries, applies the mask when present, and propagates default ACLs to child directories. It stores the inherited ACL under the child inode's write lock and restores mode/UID/GID on failure.

`ufs_acl_setattr` keeps ACL state consistent with chmod/chown/chgrp. It copies the current ACL, updates owner permissions, mask-or-group permissions, other permissions, owner UID, and group GID as requested by the `vattr`, then stores the modified ACL.

The ACL cache uses two hash tables protected by `si_cache_lock`: `si_cachea` by ACL signature/content for deduplication, and `si_cachei` by shadow inode for loading. Individual `si_t` objects use `s_lock`, `s_ref` tracks in-memory references, and `s_use` tracks shadow inode link count. `si_cache_del` carefully removes only zero-reference entries while avoiding a known race where another thread may already have deleted or reattached the ACL. `ufs_si_cache_flush` removes all ACLs for a device, and `ufs_si_del` detaches an ACL from an in-core inode.

Integration notes: ACL correctness depends on shadow inode link counts matching `s_use`, in-memory references matching `s_ref`, and releasing `s_lock` before `VN_RELE` paths that can reacquire inode locks. Shadow inodes intentionally have no quota records. Cache lookup by signature is only a candidate filter; exact ACL comparison is still required.
