# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sfbuf.c

This file implements `sf_buf` allocation and reference handling for sendfile-style page mappings. It uses `objcache` to cache `struct sf_buf` objects and `lwbuf` to map VM pages.

Important functions:
- `sf_buf_init()` creates the `sf_buf` object cache at `SI_BOOT2_MACHDEP`.
- `sf_buf_cache_ctor()` initializes cached objects with no `lwbuf` and a zero refcount.
- `sf_buf_alloc(struct vm_page *m)` gets an `sf_buf` from the cache, maps the page with `lwbuf_alloc()`, marks the lwbuf global to force TLB invalidation on all CPUs, and initializes the reference count to 1.
- `sf_buf_ref()` increments the reference count.
- `sf_buf_free()` releases a reference and, on last release, frees the lwbuf mapping and returns the `sf_buf` to the cache.

Filesystem/storage relevance:
- This is directly relevant to zero-copy file transmission and page-backed I/O paths. It bridges VM pages and temporary kernel mappings for sendfile-style operations.
