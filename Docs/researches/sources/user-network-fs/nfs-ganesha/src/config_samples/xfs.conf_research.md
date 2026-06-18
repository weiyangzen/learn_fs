<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/xfs.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/xfs.conf

Purpose: minimal sample export for the XFS-specific FSAL.

Important config surface: one `EXPORT` with id `77`, `Path = /xfs`, `Pseudo = /xfs`, RW access, and `FSAL { Name = XFS; }`.

Control flow/state: Ganesha serves the configured XFS path via FSAL_XFS. Persistent state is the underlying XFS filesystem; this file only supplies daemon configuration.

Dependencies/integration: requires FSAL_XFS support and an XFS-backed path mounted at `/xfs` or an edited equivalent. NFS clients consume the pseudo path.

Risks: assumes `/xfs` exists and is appropriate to export. The sample omits client and security hardening. XFS-specific behavior may diverge from generic VFS tests, so backend-specific validation matters.

Test signals: export an actual XFS directory, mount it, and verify inode/filehandle stability, create/read/write/remove behavior, and daemon logs during startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/xfs.conf -->
