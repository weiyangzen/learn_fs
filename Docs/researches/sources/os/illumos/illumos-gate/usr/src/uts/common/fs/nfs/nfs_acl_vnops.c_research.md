# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_vnops.c

## Purpose

This file implements client-side vnode ACL operations for the NFS ACL side protocol. It sends NFS ACL RPCs over the wire, integrates returned attributes into the NFS attribute cache, maintains per-rnode ACL caches, and implements hidden extended-attribute-directory lookup for NFSv2 and NFSv3 clients.

## Main Responsibilities

- NFS ACL v2 client operations:
  - `acl_getacl2()`
  - `acl_setacl2()`
  - `acl_getattr2_otw()`
  - `acl_access2()`
  - `acl_getxattrdir2()`
- NFS ACL v3 client operations:
  - `acl_getacl3()`
  - `acl_setacl3()`
  - `acl_getxattrdir3()`
- ACL cache management:
  - `nfs_acl_free()`
  - `nfs_acl_dup_cache()`
  - `nfs_acl_dup_res_impl()`
  - `nfs_acl_dup_res()`
- RPC metadata tables:
  - `aclnames_v2`
  - `acl_call_type_v2`
  - `acl_timer_type_v2`
  - `acl_ss_call_type_v2`
  - `aclnames_v3`
  - `acl_call_type_v3`
  - `acl_ss_call_type_v3`
  - `acl_timer_type_v3`

## Important Control Flow

`acl_getacl2()` and `acl_getacl3()`:

1. Check `rnode_t::r_secattr` for a cached ACL.
2. Validate caches with `nfs_validate_caches()` or `nfs3_validate_caches()`.
3. If the cached ACL covers the requested mask, duplicate it into the caller’s `vsecattr_t`.
4. Otherwise send `ACLPROC2_GETACL` or `ACLPROC3_GETACL`.
5. Cache returned file attributes.
6. Duplicate returned ACLs into the rnode cache with `nfs_acl_dup_res()`.
7. Return the RPC-owned ACL arrays to the caller by assigning `*vsp = res.resok.acl`.

`acl_setacl2()` and `acl_setacl3()`:

- Send SETACL over the wire.
- Always flush `rp->r_secattr` afterward because using SETACL input as cache content is not reliable and errors make existing cache contents unsafe.
- Cache returned attributes on success or post-op attributes on v3 failure.

`acl_access2()`:

- Converts vnode mode bits into ACL protocol access bits.
- Checks local access cache with `nfs_access_check()`.
- Uses `crnetadjust()` to retry with adjusted network credentials if a cached or remote denial may be credential-shape dependent.
- Sends `ACLPROC2_ACCESS` if no decisive cache entry exists.
- Stores returned access results with `nfs_access_cache()`.

`acl_getxattrdir2()` and `acl_getxattrdir3()`:

- Send GETXATTRDIR over the wire.
- Create NFS client vnodes with `makenfsnode()` or `makenfs3node()`.
- Mark returned vnode with `V_XATTRDIR`.
- Update DNLC with `XATTR_DIR_NAME` unless this was a soft failover-style call.
- On `ENOENT`, optionally negative-cache the lookup with `DNLC_NO_VNODE`.

## State and Memory Ownership

- `rnode_t::r_secattr` is protected by `r_statelock`.
- `nfs_acl_dup_cache()` allocates new ACL arrays for the caller when satisfying from cache.
- `nfs_acl_dup_res_impl()` updates or allocates the rnode cache, resizing cached ACL/default-ACL arrays when counts change.
- `nfs_acl_free()` frees both ACL arrays and the `vsecattr_t` wrapper.
- `acl_getacl2()` and `acl_getacl3()` transfer successful result ACL arrays to the caller by assigning `*vsp`; the caller is responsible for freeing them.
- `xattr_lookup_neg_cache` controls whether missing xattr directory lookups are negative-cached.

## Dependencies

- RPC call helpers:
  - `acl2call`
  - `acl3call`
- XDR routines from `nfs_acl_xdr.c`.
- NFS client helpers:
  - `nfs_cache_fattr`
  - `nfs3_cache_post_op_attr`
  - `makenfsnode`
  - `makenfs3node`
  - `nfs_access_check`
  - `nfs_access_cache`
  - `PURGE_STALE_FH`
- Failover support:
  - `failinfo_t`
  - `nfscopyfh`, `nfs3copyfh`
  - `nfslookup`, `nfs3lookup`
  - xattr dir callback pointers.
- DNLC:
  - `dnlc_update`
  - `dnlc_enter`

## Risks and Edge Cases

- ACL cache duplication must keep mask/count/data consistency; `nfs_acl_dup_res_impl()` explicitly clears cached ACL data when counts change.
- `acl_access2()` has subtle credential ownership behavior: adjusted credentials cached into access cache must not be freed prematurely.
- v3 xattr-dir creation handles missing post-op attributes by creating a vnode without attrs and then fetching `AT_TYPE` if vnode type is `VNON`.
- Negative xattr-dir caching is tunable via `xattr_lookup_neg_cache`.
- SETACL cache invalidation is intentionally conservative.

## Testing Notes

Useful coverage should include:

- ACL cache hit and cache miss paths.
- Partial mask cache hits and misses.
- SETACL invalidating cached ACLs.
- ACCESS cache allowed, denied, and unknown paths.
- Credential-adjusted retry behavior.
- GETXATTRDIR v2/v3 success, `ENOENT`, negative caching, and failover flags.
- v3 GETACL/SETACL post-op attribute handling.
