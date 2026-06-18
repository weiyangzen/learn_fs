# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_auth_xdr.c

## Purpose

This file provides XDR routines for kernel-to-mountd NFS authorization door messages. It serializes the versioned authorization request and the authorization response used by `nfs_auth.c`.

## Main Responsibilities

- `xdr_varg()`
  - Serializes a versioned argument wrapper.
  - Supports `V_PROTO`.
  - Marks unsupported versions as `V_ERROR` and fails.
- `xdr_nfsauth_arg()`
  - Serializes an authorization request:
    - command
    - client network object
    - netid
    - export path
    - requested security flavor
    - client uid
    - client gid
    - client supplemental groups
- `xdr_nfsauth_res()`
  - Serializes an authorization response:
    - daemon status
    - authorization permission bits
    - mapped server uid
    - mapped server gid
    - mapped server supplemental groups

## Dependencies

- Includes:
  - `<nfs/auth.h>`
  - `<rpc/auth_sys.h>`
- Uses standard XDR helpers:
  - `xdr_u_int`
  - `xdr_netobj`
  - `xdr_string`
  - `xdr_int`
  - `xdr_uid_t`
  - `xdr_gid_t`
  - `xdr_array`

## State and Memory Ownership

This file maintains no state. Supplemental group arrays are encoded/decoded through `xdr_array()` with `NGROUPS_UMAX` as the maximum count. On decode, XDR owns allocation semantics until callers free with `xdr_free()` or copy the data.

## Risks and Edge Cases

- `xdr_varg()` intentionally fails unknown versions and mutates `vap->vers` to `V_ERROR`.
- `req_netid` has an unbounded `~0` XDR string limit, while `req_path` is capped at `A_MAXPATH`.
- Supplemental groups are capped at `NGROUPS_UMAX`, matching auth_sys group constraints.
- The response decoder must be paired with `xdr_free(xdr_nfsauth_res, ...)` after decoded group arrays are copied or discarded.

## Integration Notes

`nfs_auth.c` uses these routines to:

1. Compute request size with `xdr_sizeof(xdr_varg, &varg)`.
2. Encode a `varg_t` into a door request buffer.
3. Decode `nfsauth_res_t` from mountd’s door response.
4. Copy mapped identity/group data out of the decoded response before freeing XDR-owned memory.
