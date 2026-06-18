# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_xdr.c

## Purpose

This file contains XDR routines for the NFS ACL side protocol, covering ACL protocol v2 and v3 arguments/results plus shared ACL security attribute structures.

## Main Responsibilities

- Encode/decode basic ACL protocol types:
  - `xdr_uid()`
  - `xdr_o_mode()`
  - `xdr_aclent()`
  - `xdr_secattr()`
- Encode/decode NFS ACL v2 procedures:
  - GETACL
  - SETACL
  - GETATTR
  - ACCESS
  - GETXATTRDIR
- Encode/decode NFS ACL v3 procedures:
  - GETACL
  - SETACL
  - GETXATTRDIR
- Provide fast inline decode helpers for selected v2 arguments/results on supported paths:
  - `xdr_fastGETACL2args()`
  - `xdr_fastGETATTR2args()`
  - `xdr_fastACCESS2args()`
  - little-endian fast result helpers for fattrs and enums.

## Important Control Flow

`xdr_secattr()` serializes:

1. `vsa_mask`
2. `vsa_aclcnt`
3. ACL entry array, bounded by `NFS_ACL_MAX_ENTRIES`
4. `vsa_dfaclcnt`
5. default ACL entry array, bounded by `NFS_ACL_MAX_ENTRIES`

It derives the outgoing array count from whether the pointer is non-NULL. After XDR, it validates that the decoded/encoded count matches the advertised count when count is non-zero; on mismatch it stores the actual count back into the count field before returning `FALSE`.

v2 result routines:

- Encode/decode enum status.
- Only serialize `resok` on `NFS_OK`.

v3 argument routines:

- Use `xdr_nfs_fh3()` for encode/free.
- Use `xdr_nfs_fh3_server()` for decode to get server-side file-handle representation.

v3 result routines:

- Serialize post-op attributes on both success and failure for GETACL and SETACL.
- GETXATTRDIR success serializes the file handle using `xdr_nfs_fh3_server()` on encode and `xdr_nfs_fh3()` on decode/free.

## Dependencies

- Common NFS XDR:
  - `xdr_fhandle`
  - `xdr_fattr`
  - `xdr_fastfattr`
  - `xdr_fastenum`
  - `xdr_nfs_fh3`
  - `xdr_nfs_fh3_server`
  - `xdr_post_op_attr`
- ACL structures:
  - `aclent_t`
  - `vsecattr_t`
  - `NFS_ACL_MAX_ENTRIES`
- Protocol types from `<nfs/nfs_acl.h>`.

## State and Memory Ownership

This file has no persistent state. Memory allocation/free for ACL arrays is handled through `xdr_array()` based on the XDR operation. Decode allocates array storage when needed; free releases it through the same XDR routines.

## Risks and Edge Cases

- Fast inline decoders only work for `XDR_DECODE` and only when `XDR_INLINE()` returns enough contiguous data; otherwise they return `FALSE`.
- Little-endian fast paths manually convert inline fields with `ntohl()`.
- `xdr_secattr()` rejects count mismatches and updates the count to the actual XDR array count before failing, which helps cleanup but can surprise callers expecting original counts to remain unchanged.
- Several max lengths use `~0` for strings/byte arrays in surrounding helpers, but ACL arrays are bounded by `NFS_ACL_MAX_ENTRIES`.
- `xdr_GETXATTRDIR3res()` switches success on `NFS_OK` rather than `NFS3_OK`; both are success-zero constants in this codebase, but the mixed naming is a maintenance hazard.

## Testing Notes

Useful tests should cover:

- XDR encode/decode/free of `vsecattr_t` with ACL and default ACL arrays.
- Count mismatch behavior in `xdr_secattr()`.
- v2 fast inline decoders on little-endian and big-endian builds.
- v3 file-handle encode/decode mode-specific behavior.
- Failure result post-op attribute serialization for v3.
