# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_attr.c

## Summary
Provides NFSv4 attribute translation support for the illumos client. It maps local `vattr_t`/`vsecattr_t` fields into encoded NFSv4 `fattr4` blobs for SETATTR, CREATE, OPEN, VERIFY, and NVERIFY operations, and defines the central NFSv4 attribute mapping table.

## Main Responsibilities
- Converts client-side set/verify attributes into XDR-encoded `fattr4` data.
- Maps local `vattr_t.va_mask` bits to NFSv4 attribute bitmaps.
- Special-cases settable atime/mtime attributes through `settime4`.
- Converts UID/GID numeric ids to NFSv4 owner/owner_group strings.
- Encodes ACL attributes supplied via `vsecattr_t`.
- Frees encoded `fattr4` payloads safely.
- Defines `nfs4_ntov_map[]`, the per-attribute mapping metadata used by attribute code.

## Key APIs
- `vattr_to_fattr4()`.
- `nfs4_fattr4_free()`.
- `nfs4_vmask_to_nmask()`.
- `nfs4_vmask_to_nmask_set()`.
- Global `nfs4_ntov_map[]` and `nfs4_ntov_map_size`.
- Global `nf4_to_vt[]`.

## Important Behavior
`vattr_to_fattr4()` selects a conversion function based on operation type. SETATTR, CREATE, and OPEN use set semantics and convert `AT_ATIME`/`AT_MTIME` to `FATTR4_TIME_ACCESS_SET`/`FATTR4_TIME_MODIFY_SET`; verify/nverify use normal read attribute semantics and convert time fields to `FATTR4_TIME_ACCESS`, `FATTR4_TIME_MODIFY`, or `FATTR4_TIME_METADATA`.

The output attribute mask is intersected with the server-supported bitmap before encoding. For verify/nverify, the code also masks out `FATTR4_CHANGE_MASK` because the local verify encoder cannot generate a `change` argument even though `nfs4_vmask_to_nmask()` adds it for ctime/mtime requests.

XDR buffer sizing is computed before encoding. Fixed-size attributes use `nfs4_ntov_map[i].xdr_size`. Variable-size owner/group strings and ACLs are manually sized with XDR length words plus rounded UTF-8 string payloads. For server-time atime/mtime SETATTR operations, the XDR size is reduced because no client timestamp is encoded.

ACL encoding is selected by the `FATTR4_ACL_MASK` table entry, whose local `vbit` is zero. The code therefore explicitly checks both `vbit` and `fbit` so ACLs are not skipped just because no `vattr_t` bit represents them.

`nfs4_fattr4_free()` clears both mask and payload pointers. It is written to tolerate repeated cleanup on partially encoded readdir entries whose attribute payload may already have been freed.

## Mapping Table
`nfs4_ntov_map[]` describes every NFSv4 attribute known to this client, including its bitmap bit, local `vattr_t` bit if any, whether it is VFS-stat-like, whether it is mandatory, numeric FATTR4 id, static XDR size, XDR function, server getter placeholder, and printable name.

The table includes mandatory protocol attributes, optional ACL and filesystem attributes, quota/space attributes, owner/group strings, raw device data, access/modify/metadata times, mounted-on fileid, and a local extension entry for `FATTR4_SUPPATTR_EXCLCREAT_MASK_LOCAL`.

## State and Lifetime
`vattr_to_fattr4()` allocates a temporary array of `union nfs4_attr_u` sized to `nfs4_ntov_map_size`, then allocates the final XDR buffer only if at least one attribute is going out. Owner and owner_group UTF-8 buffers returned by idmapping are freed after encoding. If encoding or idmapping fails, `nfs4_fattr4_free()` releases the partially constructed output.

## Dependencies
Relies on NFSv4 XDR routines stored in `nfs4_ntov_map[]`, `nfs4_time_vton()`, `nfs_idmap_uid_str()`, `nfs_idmap_gid_str()`, kmem allocation, and local NFS attribute mask constants.

## Risks
The attribute order and table index relationship are important: `amap[]` stores `nfs4_ntov_map[i].nval` and later indexes `nfs4_ntov_map[amap[i]]`. This assumes FATTR4 numeric IDs correspond to table indexes for all emitted attributes.

Manual XDR sizing for ACLs must stay in sync with `xdr_fattr4_acl()`. Any change to `nfsace4` wire encoding or string handling needs matching size accounting.

Verify/nverify support is incomplete for attributes that do not map directly to `vattr_t`; the file documents this as a known limitation for mandatory-only servers.
