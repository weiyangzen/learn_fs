# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unix_cache.c

Purpose: Generic POSIX persistent-cache implementation for Ghostscript.

Data model: A `gp_cache_entry` records cache type, key bytes, MD5 hash, filename, payload buffer/length, dirty state, and last-used time. Cache files are named as two hex type digits plus a dot plus the 16-byte MD5 digest in hex. The index file is `gs_cache` under the cache prefix.

Path and persistence flow: `gp_cache_prefix` gets `GS_CACHE_DIR`, falls back to compile-time `GS_CACHE_DIR` or `.cache`, and expands leading `~` using `HOME`. `gp_cache_indexfilename` and `gp_cache_itempath` use `gp_file_name_combine`. `gp_cache_saveitem` writes version, key length, key, data length, and data; `gp_cache_loaditem` verifies version, key length, and full key despite locating by hash.

Public operations: `gp_cache_insert` writes the payload file, rewrites the index to update or append the entry, then replaces the old index with `rename`. `gp_cache_query` loads a matching payload, updates last-used metadata in the index, and returns the loaded length plus allocated buffer.

Dependencies and notes: Uses `malloc/free`, `fopen`, `unlink`, `rename`, `time`, Ghostscript getenv/path helpers, and `md5.h`. It assumes the cache directory and index already exist; several failure paths return without freeing all intermediate allocations.
