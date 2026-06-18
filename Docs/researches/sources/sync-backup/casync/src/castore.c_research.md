# sources/sync-backup/casync/src/castore.c

## Purpose
`castore.c` implements a filesystem-backed chunk store. It can read, validate, write, test, and iterate `.cacnk` chunk files, with optional temporary-cache cleanup and configurable compression/digest behavior.

## Important APIs, Types, and Functions
`struct CaStore` stores the root path, cache/mkdir flags, reusable read buffer, validation digest/buffer, desired store compression, compression type, and request counters. `ca_store_new()` creates a normal compressed store; `ca_store_new_cache()` creates a temporary cache with as-is compression. `ca_store_get()` loads a chunk via `ca_chunk_file_load()`, decompresses for validation if needed, verifies the chunk ID using an explicit or autodetected digest, returns the stored representation, and updates counters. `ca_store_put()` lazily creates a cache root if needed and saves via `ca_chunk_file_save()`. `ca_store_has()` calls `ca_chunk_file_test()`. `CaStoreIterator` walks subdirectories and returns `.cacnk` file entries.

## Control Flow
Callers set a path or rely on cache auto-allocation, then call get/has/put. Reads always empty and reuse the internal buffer before loading. Writes create the root directory once, then delegate naming/compression details to chunk-file helpers. Iteration opens the root directory, then each subdirectory, skipping entries that are not regular chunk files with `.cacnk` suffix.

## State and Persistence
Normal stores persist under the configured root. Cache stores auto-create a random directory under `var_tmp_dir()` and delete it on unref. Reusable buffers mean returned chunk data remains valid only until the next store operation. Counters track successful read requests and bytes returned.

## Dependencies and Integration Points
The module depends on chunk helpers, digest/compression helpers, directory iteration utilities, rm-rf, and realloc buffers. It is used by `casync.c`, `casync-tool.c`, and `gc.h` for chunk storage and garbage collection.

## Risks
`ca_store_get()` returns `r` from the last digest operation, which is normally `0`, after successful load; callers expecting positive success need to follow the actual contract. Autodigest fallback can accept chunks written with any supported digest unless explicitly pinned. Iterator error handling appears suspicious: if `openat()` fails because an entry is not a directory, checking `errno == EISDIR` will not skip regular files; `ENOTDIR` would be expected. Returned data is invalidated by subsequent calls.

## Test Signals
`test/test-casync.c` exercises store put/get indirectly through full encode/decode. Additional tests should directly cover compressed/uncompressed read validation, digest pinning, cache cleanup, iterator traversal, and malformed chunks.
