# File Research: sources/os/linux/linux-stable/fs/nfsd/Kconfig

Purpose: Declares kernel configuration options for the in-kernel NFS server.

Key responsibilities:
- Defines `NFSD` core server support and its dependencies/selects.
- Exposes deprecated NFSv2 support and v2/v3 ACL protocol options.
- Exposes NFSv4 server support and dependent features.
- Defines pNFS layout options:
  - block layouts,
  - SCSI layouts,
  - flexfile layouts.
- Defines NFSv4.2 inter-server server-to-server COPY support.
- Defines NFSv4 security labels.
- Defines deprecated legacy client tracking.
- Defines experimental NFSv4 POSIX draft ACL support.

Integration:
- Drives compilation in `fs/nfsd/Makefile` and shared `fs/nfs_common` objects.
- Selects support libraries including SUNRPC, LOCKD, EXPORTFS, NFS_COMMON, GRACE_PERIOD, RPCSEC_GSS, and NFS SSC helper.

Risks and notes:
- Several options are explicitly deprecated or experimental.
- NFSv3 server support is always present when `NFSD` is selected.
