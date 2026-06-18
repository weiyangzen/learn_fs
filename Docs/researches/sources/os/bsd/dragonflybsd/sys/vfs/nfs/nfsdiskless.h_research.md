# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsdiskless.h

## Purpose

`nfsdiskless.h` defines boot-time data structures used to bring up an NFS-root or diskless DragonFlyBSD client. These structures carry network interface, gateway, server address, root/swap path, file-handle, credential, and hostname data from bootstrap code into `nfs_mountroot()`.

## Main Contents

- `struct nfsv3_diskless` is the current NFSv3-capable diskless configuration:
  - default interface and gateway,
  - NFS mount args and variable-length file handles for swap and root,
  - server socket addresses and hostnames,
  - swap block count and credentials,
  - root timestamp and client hostname.
- `struct onfs_args` preserves old pre-current NFS mount argument layout.
- `struct nfs_diskless` preserves the older NFSv2-style diskless boot structure with fixed 32-byte root/swap file handles.

## Notable Details

- The header documents that fields are stored in network byte order to avoid client/server byte-order issues.
- The newer `nfsv3_diskless` can hold up to `NFSX_V3FHMAX` file handles, while the legacy structure is fixed to `NFSX_V2FH`.
- Runtime conversion from `nfs_diskless` to `nfsv3_diskless` is implemented in `nfs_vfsops.c`.

## Integration

Consumed by `nfs_vfsops.c` for NFS root mounting and legacy diskless-boot conversion. It depends on NFS argument and protocol constants from the surrounding NFS headers.
