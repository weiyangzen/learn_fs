# File Research: sources/os/linux/linux/fs/nfs/mount_clnt.c

## Purpose
Implements the in-kernel NFS MOUNT protocol client used by NFSv2/v3 mounts to obtain a root file handle and optional auth flavor list from mountd.

## Main Entry Point
- `nfs_mount()` validates the export path length, creates a temporary MOUNT RPC client, selects v1 or v3 MOUNT procedure, sends `MOUNTPROC_MNT` with soft timeout behavior, copies the returned file handle, and fills auth flavors.
- If the server does not provide auth flavors or the protocol is not MOUNT v3, it fakes a permissive one-entry `RPC_AUTH_NULL` flavor list.

## XDR Encoding and Decoding
- `encode_mntdirpath()` encodes the export path.
- v1/v2 decode path maps OpenGroup XNFS MOUNT statuses and decodes fixed-size `NFS2_FHSIZE` file handles.
- v3 decode path maps RFC 1813 statuses, decodes variable-size file handles, rejects zero or oversized handles, and decodes up to `NFS_MAX_SECFLAVORS`.

## RPC Tables
Defines procedure tables for MOUNT v1 and MOUNT v3, exposes only MOUNT and UMOUNT procedures in this client, and registers them under the `mount` RPC program.

## Research Notes
This file is mount-bootstrap infrastructure, not regular file I/O. Its important edge handling is path length validation, file handle validation, status-to-errno mapping, and auth-flavor fallback.
