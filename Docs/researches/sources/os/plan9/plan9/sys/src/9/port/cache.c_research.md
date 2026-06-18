# File Research: sources/os/plan9/plan9/sys/src/9/port/cache.c

This file implements a page-backed file data cache for mount channels.

Key responsibilities:
- Defines `Mntcache` entries keyed by qid/dev/type and linked in an LRU list.
- Represents cached byte ranges as `Extent` records pointing to cached `Page`s in the private `fscache` image.
- `cinit` allocates file cache headers and scales `maxcache` based on memory size.
- `copen` attaches a channel to an existing cache entry or recycles an LRU entry.
- `cread` copies cached extents into a caller buffer when present and contiguous.
- `cupdate` inserts data read from a server into the cache without invalidating unrelated ranges.
- `cwrite` updates/invalidate-overwrites cached data and bumps qid versions.
- `cnodata` invalidates all extents for a cached file.

Important implementation details:
- The cache only handles non-directory, non-append files.
- It uses `kmap` to access cached pages and `lookpage/cachepage/putpage` to integrate with the page cache.
- Cached ranges are capped by `maxcache`.
- Extent records are pooled separately through `Ecache`.

Filesystem/storage relevance:
- Directly part of Plan 9’s mounted-file caching path.
- Bridges VFS channel identity, qid versioning, and VM page storage.
