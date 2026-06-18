# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_idmap.c

Purpose: Maps NFSv4 owner/group UTF-8 strings to local uid/gid values and back, with per-zone caches and nfsmapid door upcalls.

Key behavior:
- Initializes module-wide idmap cache storage, per-zone `nfsidmap_globals`, daemon door handles, and four caches: uid-to-string, string-to-uid, gid-to-string, string-to-gid.
- `nfs_idmap_str_uid` and `nfs_idmap_str_gid` convert owner strings to local IDs using literal numeric fallback, cache lookup, or nfsmapid door upcall.
- `nfs_idmap_uid_str` and `nfs_idmap_gid_str` convert local IDs to UTF-8 owner/group strings, special-casing nobody and falling back to stringified IDs when the daemon is unavailable.
- `nfs_idmap_args` flushes caches, installs a new daemon door handle, purges DNLC, and invalidates NFSv4 rnode attributes when nfsmapid re-establishes itself.
- Cache lookup/insert routines maintain per-bucket LRU lists, evict timed-out entries, and throttle eviction while the daemon is down.
- Literal helpers parse numeric stringified IDs and format numeric IDs into UTF-8 strings.

Dependencies:
- Uses zones, door kernel upcalls, nfsmapid protocol structs, DNLC purge, NFSv4 rnode invalidation, UTF-8 conversion helpers, kmem caches, per-bucket mutexes, and `pkp_tab_hash`.

Notable details:
- Server-side SETATTR mapping failures must return errors instead of silently mapping named owners to nobody, avoiding accidental ownership changes.
- Client-side unmappable strings generally map to `UID_NOBODY`/`GID_NOBODY`; server-side invalid named strings return errors such as `EPERM` or `ECOMM`.
- The daemon’s own process avoids recursive upcalls and returns `ENOTSUP` for literal numeric mappings that should not be cached.
