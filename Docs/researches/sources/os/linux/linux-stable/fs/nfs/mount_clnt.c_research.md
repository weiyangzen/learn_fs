# File Research: sources/os/linux/linux-stable/fs/nfs/mount_clnt.c

## Purpose
Implements the in-kernel NFS MOUNT protocol client used by NFSv2/v3 mounts to obtain a root file handle and optional auth flavor list from the server's mount daemon.

## Main Entry Point
- `nfs_mount(struct nfs_mount_request *info, int timeo, int retrans)`
  - Validates `dirpath` against `MNTPATHLEN`.
  - Builds a temporary RPC client for the MOUNT program.
  - Selects v1 or v3 MOUNT procedure based on `info->version`.
  - Sends `MOUNTPROC_MNT` with soft timeout behavior.
  - Copies returned file handle into caller-provided `nfs_fh`.
  - Populates auth flavors for v3; if no flavors are returned or protocol is not v3, fakes a permissive single `RPC_AUTH_NULL` flavor.

## XDR Encoding
- `encode_mntdirpath()` encodes the export path as an opaque string.
- `mnt_xdr_enc_dirpath()` is the RPC encoder wrapper.

## XDR Decoding
- v1/v2 style:
  - `decode_status()` maps OpenGroup XNFS MOUNT status values to Linux errno.
  - `decode_fhandle()` decodes fixed-size `NFS2_FHSIZE` file handles.
  - `mnt_xdr_dec_mountres()` combines status and file handle decode.
- v3:
  - `decode_fhs_status()` maps RFC 1813 MOUNT v3 status values.
  - `decode_fhandle3()` decodes variable-size v3 file handles and rejects zero or too-large handles.
  - `decode_auth_flavors()` decodes up to `NFS_MAX_SECFLAVORS`, capped by caller capacity.
  - `mnt_xdr_dec_mountres3()` combines v3 status, file handle, and auth flavor decoding.

## RPC Program Tables
- Defines v1 procedures for `MOUNT` and `UMOUNT`.
- Defines v3 procedures for `MOUNT` and `UMOUNT`.
- Registers local static `mnt_program` with program number `NFS_MNT_PROGRAM`.

## Research Notes
The error mapping is intentionally protocol-specific and avoids trusting server-local errno values. The auth flavor list is capped because RFC 1813 does not impose a practical maximum.
