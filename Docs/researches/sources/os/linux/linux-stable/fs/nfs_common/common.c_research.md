# File Research: sources/os/linux/linux-stable/fs/nfs_common/common.c

Purpose: Provides shared NFS status-code translation helpers.

Key responsibilities:
- Maps NFSv2/v3 status codes to Linux negative errno via `nfs_stat_to_errno`.
- Maps NFSv4 status codes to Linux errno via `nfs4_stat_to_errno`, using common and v4-specific tables.
- Maps Linux errno to NFSv4 status for LOCALIO via `nfs_localio_errno_to_nfs4_stat`.

Integration:
- Exported GPL symbols used by NFS client, NFSD, and localio paths.
- Includes localio-specific mappings where errno-to-NFS status differs from normal NFSv4 decode tables.

Risks and notes:
- Unknown v2/v3 statuses become `-EIO`.
- Unknown out-of-range v4 statuses become `-EREMOTEIO`; otherwise untranslated v4 statuses may be returned as `-stat` for recovery paths.
