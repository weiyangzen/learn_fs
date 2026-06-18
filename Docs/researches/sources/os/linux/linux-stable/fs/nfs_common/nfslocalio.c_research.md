# File Research: sources/os/linux/linux-stable/fs/nfs_common/nfslocalio.c

Purpose: Implements shared NFS LOCALIO protocol-bypass support between an NFS client and a local NFSD server.

Key responsibilities:
- Maintains a global list of client UUID records during localio probing.
- Initializes, begins, and ends UUID probing lifecycle.
- Marks a UUID as local once NFSD confirms it, moving it to the NFSD net namespace local client list.
- Holds an NFSD module reference and auth domain reference while localio is active.
- Enables/disables localio client tracing.
- Invalidates all local clients during NFSD net teardown.
- Opens local filehandles through NFSD callbacks while safely acquiring NFSD net/server references.
- Tracks cached local `nfsd_file` handles per NFS file localio record.
- Closes local filehandles safely while racing with client disable.
- Exports `nfs_to`, the NFSD operation vector used by NFS localio code.

Integration:
- Depends on callbacks supplied by NFSD through `struct nfsd_localio_operations`.
- Used by NFS read/write/commit paths that can bypass RPC when client and server are local.
- Uses RCU, spinlocks, module refs, auth-domain refs, and wait-var synchronization.

Risks and notes:
- Lock ordering is explicitly documented: UUID lock, global UUID lock, then namespace local-client lock.
- Net pointer is not a counted reference; safety relies on RCU and `nfsd_net_try_get`.
- File close/disable races are coordinated through `nfl->nfs_uuid` and wait variables.
