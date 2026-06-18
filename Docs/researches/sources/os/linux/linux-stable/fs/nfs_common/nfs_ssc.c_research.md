# File Research: sources/os/linux/linux-stable/fs/nfs_common/nfs_ssc.c

Purpose: Shared registration table allowing NFSD server-side-copy code to call NFS client module operations.

Key responsibilities:
- Exports global `nfs_ssc_client_tbl`.
- Registers/unregisters NFSv4.2 client SSC ops with `nfs42_ssc_register` / `nfs42_ssc_unregister`.
- Registers/unregisters broader NFS client ops with `nfs_ssc_register` / `nfs_ssc_unregister`.
- Provides empty stubs when relevant NFSv4.2 config is disabled.

Integration:
- Bridges NFSD inter-server COPY support with NFS client implementation.
- `super.c` registers NFS client SSC ops under `CONFIG_NFS_V4_2`.

Risks and notes:
- Unregister only clears the table when the pointer matches, preventing accidental removal of replaced ops.
