# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsdiskless.h

This header defines diskless NFS root boot structures.

Key contents:
- Documents that diskless structures are used by NFS root mount setup and partial interface/route configuration.
- `struct nfsv3_diskless` supports NFSv3 file handles up to `NFSX_V3FHMAX` and stores interface alias, gateway, root mount args, server address, root path, root timestamp, and client hostname.
- `struct onfs_args` captures legacy NFS mount arguments.
- `struct nfs_diskless` is the legacy NFSv2 root configuration with fixed `NFSX_V2FH` handle.
- Kernel declarations expose `nfsv3_diskless`, `nfs_diskless`, `nfs_diskless_valid`, `bootpc_init()`, `nfs_setup_diskless()`, and `nfs_parse_options()`.

Important dependencies:
- Implemented by `nfs_diskless.c`.
- Consumed by NFS mount-root code.

Risks and notes:
- Comments state fields are stored in network byte order and currently only AF_INET is supported.
