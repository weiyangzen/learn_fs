# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unix_cache.c

Purpose: Implements a generic POSIX persistent cache for Ghostscript, storing typed key/value buffers on disk and maintaining an index file.

Key interfaces: `gp_cache_insert` and `gp_cache_query`; internal helpers compute cache directory prefixes, index filenames, MD5-derived item filenames, index entries, and serialized item payloads.

Control flow: the cache directory comes from `GS_CACHE_DIR`, compiled `GS_CACHE_DIR`, or `.cache`, with leading `~` expanded against `HOME`. Each entry hashes `(type,key)` with MD5, writes payload files named as type plus hash, and rewrites the `gs_cache` index through a `+` temporary file. Query loads and validates the payload version, key length, full key bytes, data length, and data buffer allocated by caller-supplied callback.

Dependencies: Uses `gp_getenv`, `gp_file_name_combine`, `gconfigd.h`, `md5.h`, stdio, `malloc/free/strdup`, `time`, `unlink`, and `rename`.

Risks and notes: The code assumes the index file already exists and does not create the cache directory. Several error paths leak allocated strings or open files. `gp_cache_read_entry` allocates `strlen(fn)+1` but does not copy the terminating NUL. `gp_cache_loaditem` can `memcmp` a `NULL` `filekey` if malloc fails, and read/write return values are mostly ignored.
