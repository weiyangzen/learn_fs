# File Research: sources/os/linux/linux/fs/nfs_common/nfslocalio.c

Implements shared NFS LOCALIO client/server handshake state and local file-handle open/close coordination.

Key behavior:
- Maintains a global list of `nfs_uuid_t` objects for clients probing whether their NFS server is local.
- `nfs_uuid_init()` initializes the embedded UUID state, lists, lock, and probe count.
- `nfs_uuid_begin()` ensures the UUID state is unused, adds it to the global list, and generates a UUID for discovery.
- `nfs_uuid_end()` removes an unused UUID from the global list if the client was not matched to a local server.
- `nfs_uuid_is_local()` is called by NFSD when it sees a matching UUID; it moves the UUID to the NFSD net namespace local-client list, pins the NFSD module, holds the auth domain, and publishes the local net pointer with RCU.
- `nfs_localio_enable_client()` traces enablement; actual enablement is performed by the UUID match path.
- `nfs_localio_disable_client()` tears down local state, clears the net pointer, releases auth/module references, closes cached local files, removes the client from the NFSD namespace local list, and traces disablement.
- `nfs_localio_invalidate_clients()` disables all LOCALIO clients attached to an NFSD network namespace during server teardown.
- `nfs_open_local_fh()` safely obtains an NFSD net reference, calls NFSD local-file open operations, links the cached local file into the UUID’s file list, and unwinds on races with teardown.
- `nfs_close_local_fh()` handles ordinary close, races with client teardown, local file ref drops, list removal, and wakeups for teardown waiters.
- Exports `nfs_to`, a function-pointer table populated by NFSD for LOCALIO operations.

Important interactions:
- Provides protocol bypass only when client and server are in the same kernel and a UUID handshake establishes locality.
- Uses RCU, spinlocks, module references, auth-domain references, and wait variables to keep NFSD callbacks valid during local file operations.
