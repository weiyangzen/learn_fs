# File Research: sources/os/linux/linux-stable/fs/nfs/fscache.h

## Purpose

Defines the NFS fscache/netfs interface, auxiliary cache coherency data, netfs read aggregation state, and no-op fallbacks when `CONFIG_NFS_FSCACHE` is disabled.

## API Surface

- `struct nfs_fscache_inode_auxdata`: mtime, ctime, and NFSv4 change attribute used for cache coherency.
- `struct nfs_netfs_io_data`: refcounted bridge between one netfs subrequest and potentially many NFS RPC completions.
- `nfs_netfs_get()` / `nfs_netfs_put()`: manage the bridge lifetime and final netfs termination.
- Declarations for superblock cookie, inode cookie, open/release, folio read, readahead, and pageio/netfs completion helpers.
- `nfs_fscache_release_folio()`: waits for deprecated `PG_private_2` cache writeback when needed and notes page release.
- `nfs_fscache_update_auxdata()` / `nfs_fscache_invalidate()`: build coherency metadata and invalidate cookies.
- `nfs_server_fscache_state()` and pageio header/descriptor transfer helpers.
- Disabled-config stubs return no-cache behavior and keep callers simple.

## Dependencies

Includes Linux swap, NFS mount/filesystem headers, fscache, netfs request APIs, and inode versioning.

## Risks

The enabled and disabled branches must preserve identical caller semantics. `nfs_netfs_put()` owns final netfs completion and must not run early. Folio release behavior must avoid sleeping from reclaim contexts while still waiting for cache writes when safe.
