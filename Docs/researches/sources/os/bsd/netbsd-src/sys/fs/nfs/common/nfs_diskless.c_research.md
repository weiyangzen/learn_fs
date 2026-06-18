# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_diskless.c

This file populates kernel diskless NFS root configuration from loader environment variables. It supports both legacy NFSv2-style diskless data and NFSv3 file handles.

Key contents:
- Defines global `nfs_diskless`, `nfsv3_diskless`, and `nfs_diskless_valid`.
- `nfs_parse_options()` parses root mount options such as `soft`, `intr`, `conn`, `nolockd`, `nocto`, `nfsv2`, `nfsv3`, `tcp`, `udp`, `rsize=`, and `wsize=`.
- `nfs_setup_diskless()` reads loader variables for interface IP/netmask/gateway/hardware address, NFS root server/path/options, and NFS root file handle.
- Matches the boot interface by Ethernet link-layer address, waiting up to `NFS_IFACE_TIMEOUT_SECS`.
- Fills either `nfsv3_diskless` with NFSv3 defaults or `nfs_diskless` with legacy NFSv2 defaults.
- Helper parsers convert dotted IPv4 strings, Ethernet MAC strings, and `X...X` encoded NFS handles.
- `nfs_rootconf()` can mark `rootdevnames[0] = "nfs:"` when bootp support is not handling setup.

Important dependencies:
- Consumed by NFS root mount code through `nfsdiskless.h`.
- Depends on kernel environment APIs and interface lists.

Risks and notes:
- IPv4-only and Ethernet-oriented.
- `rsize`/`wsize` validation caps values at 32 KiB.
- File-handle parsing accepts only the custom loader hex format.
