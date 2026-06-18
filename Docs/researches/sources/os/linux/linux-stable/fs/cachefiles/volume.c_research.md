# File Research: sources/os/linux/linux-stable/fs/cachefiles/volume.c

This file manages CacheFiles per-volume directory structures.

Primary flow:
- `cachefiles_acquire_volume()` allocates `struct cachefiles_volume`, binds it to the FS-Cache volume cookie and cache, constructs a volume directory name from the volume key prefixed with `I`, creates or opens that directory under `cache->store`, checks or sets volume coherency xattr, creates 256 fanout directories named `@00` through `@ff`, stores the volume in `vcookie->cache_priv`, pins FS-Cache volume access, and links the volume into `cache->volumes`.
- `cachefiles_free_volume()` removes the volume from the cache list and frees dentries/structure.
- `cachefiles_withdraw_volume()` writes the volume xattr and frees the volume structure.

Coherency:
- Newly created volume directories receive a volume xattr.
- Existing volume directories are checked against the volume coherency data.
- If an existing volume is stale (`-ESTALE`), the directory is buried and acquisition retries.

Fanout:
- Each volume pre-creates and pins 256 fanout directories. Object files are later placed under one of these by low byte of cookie key hash.

Error handling:
- Partial fanout setup unwinds by putting all created directories.
- All directory operations run under secure cache credentials.
- Weird or stale volume directories can be moved to the graveyard through `cachefiles_bury_object()`.
