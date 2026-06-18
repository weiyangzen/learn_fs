# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_acl.c

## Summary
Implements illumos NFSv4 ACL conversion, validation, comparison, cache maintenance, and idmapping safety rules. It bridges three ACL representations: POSIX draft `aclent_t`, illumos/ZFS-style `ace_t`, and wire-level `nfsace4`.

## Main Responsibilities
- Initializes kmem caches for temporary ACE aggregation structures.
- Frees `vsecattr_t` payloads containing `aclent_t`, `ace_t`, or `nfsace4` entries.
- Converts POSIX draft ACL arrays to NFSv4 ACE arrays via the NFSv4 ACL mapping draft.
- Converts NFSv4 ACE arrays back to regular/default POSIX draft ACLs when the ACE pattern is representable.
- Converts between illumos `ace_t` and `nfsace4` with owner/group string idmapping.
- Maintains the per-rnode cached NFSv4 ACL copy.
- Prevents silent mapping of non-`nobody` ACL principals to `UID_NOBODY`/`GID_NOBODY`.

## Key APIs
- `nfs4_acl_init()`.
- `vs_aent_to_ace4()` and `vs_ace4_to_aent()`.
- `vs_acet_to_ace4()` and `vs_ace4_to_acet()`.
- `vs_aent_destroy()`, `vs_ace4_destroy()`, `vs_acet_destroy()`.
- `ln_ace4_cmp()`.
- `nfs4_acl_fill_cache()` and `nfs4_acl_free_cache()`.

## Important Behavior
`ln_aent_to_ace4()` performs POSIX draft ACL to NFSv4 conversion. It preprocesses ACLs to detect sorting needs, count named users/groups, and find exactly one `CLASS_OBJ` mask when named entries require it. It emits ALLOW/DENY pairs, injects mask-emulation DENY ACEs for named users/groups and `GROUP_OBJ`, places group DENY entries after the group ALLOW sequence, and maps `USER_OBJ`, `GROUP_OBJ`, and `OTHER_OBJ` to `OWNER@`, `GROUP@`, and `EVERYONE@`.

`mode_to_ace4_access()` and `access_mask_set()` decide which NFSv4-only bits are produced for allow/deny entries. Tunable static masks split behavior between client/server produce and consume paths, especially for `ACE4_SYNCHRONIZE`, `ACE4_WRITE_OWNER`, `ACE4_DELETE`, named attributes, and write attributes.

The reverse path, `ln_ace4_to_aent()`, intentionally accepts only a constrained, POSIX-mappable ACE ordering. It rejects unsupported ACE types, illegal flags, invalid masks, partial write bit sets, unsupported inheritance patterns, out-of-order entities, duplicate ALLOW entries, unmatched ALLOW/DENY complements, and inconsistent ACL mask emulation. It aggregates named users and groups in AVL trees before producing regular and default ACL lists.

`vs_acet_to_ace4()` and `vs_ace4_to_acet()` are less restrictive than the POSIX draft mapping path. They translate individual `ace_t` entries to/from NFSv4 ACEs, preserving supported NFSv4 ACE flags and access-mask bits and mapping special principals to local owner/group/everyone flags.

`nfs4_acl_fill_cache()` deep-copies NFSv4 ACE arrays into `rnode4_t.r_secattr`. If counts match, it reuses the existing ACE array but frees and replaces each embedded `who` string. If only the ACL count is being cached, it drops any stale full ACL payload.

## State and Lifetime
`nfsace4.who.utf8string_val` strings are separately allocated and must be freed per entry. The conversion routines often copy `nfsace4` structs by value, then rely on ownership transfer of embedded `who` pointers. Error paths explicitly walk partially built arrays to free embedded strings.

`ace4_list_t` is cache-allocated and contains constructed AVL trees for named user/group aggregation. `ace4_list_free()` destroys only tree nodes and returns the container to the cache; the AVL tree headers themselves are initialized/destroyed by the cache constructor/destructor.

The rnode ACL cache is protected by `r_statelock`. Cached ACL payloads are NFSv4 ACEs only; default ACL pointer fields are not populated for this cache.

## Dependencies
Depends on illumos ACL, AVL, kmem, UTF-8, and NFS idmapping helpers: `nfs_idmap_uid_str()`, `nfs_idmap_gid_str()`, `nfs_idmap_str_uid()`, `nfs_idmap_str_gid()`, `utf8_copy()`, `str_to_utf8()`, `utf8_compare()`, and `utf8_to_str()`.

## Risks
The ACL mapping is deliberately lossy and accepts only ACE layouts that can be represented as POSIX draft ACLs. Callers must be prepared for `ENOTSUP` on valid NFSv4 ACLs outside that subset.

Client-side setters reject `UID_UNKNOWN`/`GID_UNKNOWN` in outgoing ACLs to avoid read-modify-write cycles preserving unmappable entries as real principals. Server-side idmap failures can become `NFS4ERR_BADOWNER`.

`remap_id()` assigns `GID_UNKNOWN` after the user branch without an `else`, so a user remap is overwritten to `GID_UNKNOWN`. That appears intentional only if `UID_UNKNOWN` and `GID_UNKNOWN` are identical; otherwise it is a correctness hazard.

`acet_mask_to_ace4_mask()` checks `ACE4_READ_NAMED_ATTRS` against an `ace_t` mask where the surrounding code otherwise uses `ACE_*` constants. If those constants differ, read-named-attribute permission may fail to translate correctly.
