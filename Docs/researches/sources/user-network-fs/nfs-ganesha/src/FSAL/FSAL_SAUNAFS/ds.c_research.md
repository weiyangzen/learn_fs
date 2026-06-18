# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/ds.c

This file implements SaunaFS pNFS data-server operations. It creates data-server handles from pNFS wire handles, opens/caches SaunaFS file handles for direct I/O, services DS read/write/commit calls, and installs the DS operation vector.

Important functions are `clearFileInfoCache`, `dsh_release`, `openfile`, `dsh_read`, `dsh_write`, `dsh_commit`, `dsh_read_plus`, `make_ds_handle`, `ds_permissions`, and `pnfsDsOperationsInit`. `struct DataServerHandle` stores the public `fsal_ds_handle`, inode, and an optional `FileInfoEntry_t` from the export-level fileinfo cache. `struct DSWire` is the client-visible DS wire payload containing the inode.

Control flow for I/O starts with `make_ds_handle`, which validates and endian-converts the inode from the wire buffer. `dsh_read`/`dsh_write` locate the MDS FSAL export through `op_ctx->ctx_pnfs_ds`, call `openfile`, extract a cached `fileinfo_t`, and invoke `saunafs_read` or `saunafs_write` with no user credentials. Writes flush when requested stability is not `UNSTABLE4`; commit flushes and returns an all-zero verifier. Release returns the cache entry to the LRU and opportunistically clears expired entries.

State is centered on `FileInfoCache_t`: DS handles retain acquired cache entries while alive; released entries can be reused or expired. Persistent file data belongs to SaunaFS. DS permissions install root export permissions in `op_ctx`.

Dependencies include pNFS DS defaults, Ganesha export context, the SaunaFS wrappers, and the fileinfo cache. Risks include weak stateid validation, `dsh_commit` returning OK if opening fails, no READ_PLUS support, credential-null I/O semantics, and cache correctness under concurrent DS handles. Test signals should cover endian wire handles, bad handles, repeated read/write sharing a cached fileinfo, cache expiry, stable write flush failures, DS permission behavior, and NFSv4.2 READ_PLUS rejection.
