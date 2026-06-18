# sources/sync-backup/casync/src/caseed.c

## Purpose
`caseed.c` builds and serves a local seed cache from an existing filesystem tree or file. It runs a `CaEncoder`, chunk-splits emitted payload bytes, records chunk ID to source-location mappings, optionally records hardlink targets, and later serves matching chunks by seeking back into the encoder source and revalidating content.

## Important APIs, Types, and Functions
`struct CaSeed` stores the encoder, base/cache fds and path, chunker, digest, mode flags, pending chunk buffer and location, file root, feature flags, counters, and timing. `ca_seed_open()` initializes the encoder and cache directory. `ca_seed_cache_chunks()` scans encoder data through `ca_chunker_scan()`, buffers chunk spans across encoder data boundaries, and writes cache entries. `ca_seed_write_cache_entry()` computes the chunk ID, formats a full `CaLocation`, and stores it as a symlink or fallback file under `<first4>/<id>`. `ca_seed_cache_hardlink()` maps hardlink digests to entry locations. `ca_seed_step()` advances the encoder and updates the cache. `ca_seed_get()` looks up a chunk location, seeks the encoder, reconstructs the bytes, optionally builds a `CaOrigin`, and verifies the chunk ID before returning data.

## Control Flow
Callers configure base and cache, then call `ca_seed_step()` until `CA_SEED_READY`. During stepping, encoder events produce data, next-file, done-file, payload, or finished states. Data-bearing states feed chunk cache creation; done-file can add hardlink metadata; finished flushes a final partial chunk. Once ready or partially indexed, `ca_seed_get()` reads the cache entry, rejects unknown-size hardlink entries for normal chunk lookup, seeks the encoder, copies bytes until the requested chunk size is satisfied, validates the digest, and returns a buffer owned by the seed object.

## State and Persistence
The cache is a directory tree keyed by chunk ID prefix. Normal entries are symlinks to formatted `CaLocation` strings; too-long targets are stored as regular files. Temporary caches are removed on unref. Runtime buffers are reused, so returned data and origins must be consumed according to API ownership expectations. Timing fields record first and last seed step times.

## Dependencies and Integration Points
The module depends on chunking, digest, encoder, file root, format, location, origin, rm-rf, time, and realloc-buffer helpers. `casync.c` uses seeds to satisfy missing chunks from local data during extraction and to support hardlink/reflink optimizations.

## Risks
The seed cache can become stale if source files change; `ca_seed_get()` detects some cases via seek failures, premature EOF, and final digest mismatch returning `-ESTALE`. Cache entries stored as symlinks expose location strings in filesystem metadata and can hit `ENAMETOOLONG`, hence the regular-file fallback. `ca_seed_cache_final_chunk()` returns `0` even if `ca_seed_write_cache_entry()` fails, apparently swallowing the error. The shared `buffer` is used for both chunk assembly and serving, so reentrant use is unsafe.

## Test Signals
`test/test-nbd.sh.in` and script tests exercise seed extraction by extracting with `--seed` and comparing digests. No focused unit test for `CaSeed` internals was visible. Useful tests include stale source mutation, hardlink target lookup, long location fallback files, disabled chunk/hardlink modes, and final chunk error propagation.
