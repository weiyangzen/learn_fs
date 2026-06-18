# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_client.c

## Scope

This file contains SMBFS client-side cache validation, attribute conversion, flush-all traversal, and per-zone mount list lifecycle.

## APIs And Behavior

- `smbfs_waitfor_purge_complete()` waits interruptibly for another thread’s cache purge to finish.
- `smbfs_validate_caches()` uses the attribute cache when valid or fetches fresh attributes from the server.
- `smbfs_purge_caches()` invalidates cached vnode pages through `VOP_PUTPAGE(..., B_INVAL, ...)`.
- `smbfs_cache_check()` compares cached and fresh mtime/size/ctime to decide page-cache and ACL-cache invalidation.
- `smbfs_attrcache_fa()` stores fresh SMB attributes, computes adaptive cache expiry based on time since detected modification, updates vnode type/mode, and reconciles client-visible size.
- `smbfs_getattr_cache()` returns cached SMB attributes when not expired.
- `smbfs_getattr_otw()` fetches attributes via an existing open FID or path/attribute open, handles fake XATTR directories, prunes caches on remove/rename errors, and refreshes caches.
- `smbfsgetattr()` combines UID/GID ACL refresh, cached/remote SMB attributes, and conversion to `vattr`.
- `smbfattr_to_vattr()` maps SMB attributes to vnode attributes, including client-side size, inode number, mode, uid/gid, times, and block count.
- `smbfattr_to_xvattr()` maps SMB creation time and DOS archive/system/readonly/hidden bits to extensible attributes.
- `smbfs_flushall()` walks per-zone SMBFS mounts and calls `smbfs_rflush()`.
- Zone callbacks initialize, shut down, destroy, add, and remove per-zone mount lists.
- `smbfs_clntinit()` creates the zone key and optional callback hooks; `smbfs_clntfini()` tears them down.

## State And Dependencies

- Uses `smbnode_t` cached attributes, `r_attrtime`, `r_mtime`, `r_size`, `r_secattr`, `r_serial`, mount timeout settings, and per-zone `smi_globals`.
- Depends on SMBFS protocol helpers, vnode page cache operations, zones, lists, kstats, and ACL helpers.

## Risks And Invariants

- Attribute cache timing deliberately avoids assuming synchronized client/server clocks.
- Size updates avoid overwriting dirty or actively referenced cached file data.
- Zone destroy may defer freeing globals until late VFS teardown removes the final mount.
- `smbfs_zonelist_remove()` frees globals while holding the zone list lock on the deferred destroy path.
