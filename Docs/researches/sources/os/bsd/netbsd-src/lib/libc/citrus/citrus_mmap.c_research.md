# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mmap.c

File mapping helper for Citrus data files.

Key behavior:
- `_citrus_map_file` opens a path read-only with `O_CLOEXEC`, verifies it is a regular file, maps it private/read-only, and initializes a region over the mapping.
- On failure, returns `errno` or `EOPNOTSUPP` and closes the fd.
- `_citrus_unmap_file` unmaps and clears a non-null mapped region.

Used throughout Citrus for locale files, lookup files, DBs, ESDBs, mapper/iconv metadata, and pivot data.
