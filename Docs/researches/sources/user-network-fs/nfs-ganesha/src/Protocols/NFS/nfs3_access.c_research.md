## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_access.c

Purpose: implements NFSv3 `ACCESS`.

APIs and flow: `nfs3_access` converts the file handle to an FSAL/cache object with `nfs3_FhandleToCache`, calls `nfs_access_op` with the requested access mask, builds post-op attributes on success or access-denied, maps nonretryable errors to NFSv3 status, drops retryable errors, and releases the object ref. Free function is a no-op.

State/dependencies: read-only over object metadata and export permissions resolved by the dispatcher. Depends on NFSv3 handle conversion, FSAL access checks, and post-op attr helpers.

Risks/tests: test allowed/denied masks, stale/bad handles, retryable FSAL errors, attr-follow flags on failure, and squashed credential effects inherited from dispatcher.
