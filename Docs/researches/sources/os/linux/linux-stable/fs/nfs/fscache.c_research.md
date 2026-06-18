# File Research: sources/os/linux/linux-stable/fs/nfs/fscache.c

## Purpose

Connects the NFS client to fscache and netfs. It builds cache volume/cookie keys, manages per-inode cache cookies, enables/disables caching on file open/close, and adapts NFS pageio reads to netfs subrequests.

## Main Entry Points

- `nfs_fscache_get_super_cookie()` / `nfs_fscache_release_super_cookie()`: acquire and release per-superblock cache volumes.
- `nfs_fscache_init_inode()` / `nfs_fscache_clear_inode()`: acquire and release per-regular-file cache cookies.
- `nfs_fscache_open_file()` / `nfs_fscache_release_file()`: use/unuse cookies and invalidate cache on write-open.
- `nfs_netfs_read_folio()` / `nfs_netfs_readahead()`: enter netfs read paths when a cache cookie exists.
- `nfs_netfs_issue_read()`: split a netfs subrequest into NFS pageio folio reads.
- `nfs_netfs_initiate_read()` / `nfs_netfs_read_completion()`: reference and complete the shared netfs I/O state for NFS RPC completions.
- `nfs_netfs_ops`: netfs request operations exported to inode initialization.

## Control Flow And State

Superblock cache keys include NFS protocol version, minor version, server address, fsid, mount/server flags, I/O sizes, attribute cache timings, auth flavor, and optional fscache uniquifier. Inode cookies use the NFS filehandle as the index key plus auxiliary coherency data from mtime, ctime, and NFSv4 change attribute.

Netfs reads allocate `nfs_netfs_io_data` because one netfs subrequest may become multiple NFS RPCs. Each initiated NFS read increments the refcount; completions accumulate transferred byte counts or errors. The final put clamps the transferred length to the requested subrequest length, fills netfs completion state, and calls `netfs_read_subreq_terminated()` once.

## Dependencies

Depends on Linux fscache, netfs, xarray page iteration, NFS pageio read helpers, open contexts, inode versioning, fattr-derived coherency data, and declarations in `fscache.h`.

## Risks

Cache key construction must remain bounded and collision-resistant enough for NFS mount identity. Cache coherency depends on auxiliary data being updated before cookie invalidation/unuse. Netfs completion is refcount-sensitive: only the last NFS RPC may terminate the netfs subrequest, and overread clamping avoids netfs warnings for full-page NFS reads serving partial subrequests.
