# File Research: sources/os/linux/linux/fs/nfs_common/common.c

Provides shared NFS status-code and errno translation helpers.

Key behavior:
- `nfs_stat_to_errno()` maps NFSv2/v3 status codes to Linux negative errno values, defaulting unknown statuses to `-EIO`.
- `nfs4_stat_to_errno()` first checks common NFSv4 mappings, then extra NFSv4 mappings such as server fault, locked, illegal op, and xattr errors.
- Unknown NFSv4 status values outside the expected protocol range map to `-EREMOTEIO`; otherwise they are returned as negative protocol status so recovery paths can handle them.
- `nfs_localio_errno_to_nfs4_stat()` maps local errno values back to NFSv4 status codes for LOCALIO, using common mappings plus LOCALIO-specific corrections.

Important interactions:
- Exported for use by NFS client, NFSD, XDR decode/encode paths, and LOCALIO conversion.
- LOCALIO mappings intentionally differ from generic client mappings where errno-to-protocol translation needs server-side semantics.
