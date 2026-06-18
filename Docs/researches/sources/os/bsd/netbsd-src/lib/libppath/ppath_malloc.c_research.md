# File Research: sources/os/bsd/netbsd-src/lib/libppath/ppath_malloc.c

## Purpose
Provides allocation hooks for `libppath`.

## Main Responsibilities
- Implements `ppath_alloc(size_t)` as zero-initializing `calloc(1, size)`.
- Implements `ppath_free(void *, size_t)` as `free(p)`, ignoring size.

## Dependencies
- `stdlib.h`.
- Internal `ppath/ppath_impl.h`.
