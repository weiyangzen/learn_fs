# File Research: sources/os/linux/linux/fs/nfs/fscache.h

## Purpose
Declares and conditionally stubs NFS FS-Cache/netfs integration.

## Enabled Configuration
When `CONFIG_NFS_FSCACHE` is enabled:
- Defines `struct nfs_fscache_inode_auxdata` for cache coherency metadata.
- Defines `struct nfs_netfs_io_data` for coordinating split NFS RPC completions for one netfs subrequest.
- Provides inline refcount helpers `nfs_netfs_get()` and `nfs_netfs_put()`.
- Declares fscache and netfs functions implemented in `fscache.c`.
- Implements helper inlines for folio release, auxiliary data generation, cache invalidation, readable server cache state, and pageio/netfs pointer transfer.

## Disabled Configuration
When `CONFIG_NFS_FSCACHE` is disabled, all integration points become no-op or negative stubs:
- Inode init/clear/open/release do nothing.
- Netfs reads return `-ENOBUFS`.
- Folio unlock helper returns that NFS should unlock.
- Server fscache state reports `"no "`.

## Important Details
`nfs_fscache_release_folio()` waits for deprecated private-2 folio state unless reclaim context forbids sleeping, then notifies fscache of page release.

`nfs_fscache_update_auxdata()` uses inode mtime/ctime and NFSv4 raw i_version as coherency data.

`nfs_fscache_invalidate()` updates auxdata and calls `fscache_invalidate()` with inode size and invalidation flags.

`nfs_netfs_put()` caps final transferred length to the netfs subrequest length to avoid netfs overread warnings when NFS reads full pages for partial-page requests.

## Research Notes
This header cleanly isolates optional FS-Cache behavior. Call sites can invoke fscache/netfs hooks unconditionally while build-time configuration determines whether they are active or stubs.
