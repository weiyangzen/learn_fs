# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/cache.c

Implements allocation, initialization, loading, flushing, and destruction of a blkid cache.

Key functions:
- `blkid_get_cache(blkid_cache *ret_cache, const char *filename)`
  - Initializes debug mask from `BLKID_DEBUG` once.
  - Allocates `blkid_struct_cache`.
  - Initializes device and tag lists.
  - Chooses cache file from explicit filename, `BLKID_FILE`, or `/etc/blkid.tab`.
  - Calls `blkid_read_cache`.
- `blkid_put_cache(blkid_cache cache)`
  - Flushes changed cache with `blkid_flush_cache`.
  - Frees all cached devices and remaining tag head structures.
  - Frees cache filename and cache object.

Behavior:
- Empty filename is treated as no filename.
- `BLKID_FILE` is used only when real/effective UID match.
- Cache destruction warns under debug if tag entries remain under tag heads.

Dependencies:
- `blkid_read_cache` from `read.c`
- `blkid_flush_cache` from `save.c`
- `blkid_free_dev` from `dev.c`
- `blkid_free_tag` from `tag.c`

Notable details:
- `blkid_debug_mask` is defined globally here.
- The `TEST_PROGRAM` path creates a cache, probes all devices, and releases it.
