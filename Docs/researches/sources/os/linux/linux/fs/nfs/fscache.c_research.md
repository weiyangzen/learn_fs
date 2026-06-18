# File Research: sources/os/linux/linux/fs/nfs/fscache.c

## Purpose
Implements NFS integration with FS-Cache and the netfs read helper layer.

## Superblock Cache Volume
`nfs_fscache_get_super_cookie()` builds a cache volume key from:
- NFS protocol version/minor version.
- Server address and port.
- FSID.
- Superblock flags.
- NFS server flags.
- rsize/wsize.
- attribute cache timers.
- auth flavor.
- optional `fsc=` uniquifier.

It acquires an FS-Cache volume with `fscache_acquire_volume()` and stores it in `nfs_server.fscache`. `nfs_fscache_release_super_cookie()` relinquishes the volume and frees the uniquifier.

## Inode Cache Cookies
`nfs_fscache_init_inode()` creates filehandle-indexed cookies for regular files when the superblock has fscache enabled. It uses auxiliary coherency data from mtime, ctime, and NFSv4 change attribute, then marks the mapping for release callbacks.

`nfs_fscache_clear_inode()` relinquishes the per-inode cookie.

## Open/Close Behavior
`nfs_fscache_open_file()` uses a cookie on open. For write opens, it invalidates the cache using current auxiliary data and file size.

`nfs_fscache_release_file()` unuses the cookie and supplies updated auxiliary data and size.

## Netfs Read Integration
`nfs_netfs_read_folio()` and `nfs_netfs_readahead()` call into netfs only if the inode has a cache cookie; otherwise they return `-ENOBUFS`.

`nfs_netfs_issue_read()` turns one netfs subrequest into NFS pageio reads. It allocates `nfs_netfs_io_data`, initializes an NFS read pageio descriptor, walks the mapping xarray over requested pages, adds folios to NFS read I/O, completes pageio, and terminates the netfs subrequest through reference-counted completion.

## Completion Semantics
`nfs_netfs_io_data.refcount` ensures `netfs_read_subreq_terminated()` is called exactly once even if one netfs subrequest maps to multiple NFS RPC completions. Completion records transferred bytes or error, handles EOF tail clearing, and caps transferred length in the header inline helper.

## Netfs Ops
Exports `nfs_netfs_ops` with:
- `.init_request`
- `.free_request`
- `.issue_read`

`init_request` stores an NFS open context, assigns a debug id, uses deprecated PG_private_2 cache-write tracking, and sets max subrequest length from NFS rsize.

## Research Notes
This file is the active implementation behind the `CONFIG_NFS_FSCACHE` API declared in `fscache.h`. It links NFS pageio and FS-Cache/netfs while preserving NFS-specific open context and completion behavior.
