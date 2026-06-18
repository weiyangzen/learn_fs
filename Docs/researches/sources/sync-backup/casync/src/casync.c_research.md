# sources/sync-backup/casync/src/casync.c

## Purpose

`casync.c` is the high-level orchestration layer for casync encode and decode sessions. It owns the opaque `CaSync` object exposed by `casync.h`, wires encoders/decoders to local and remote chunk stores, indexes, archives, seeds, caches, and pollable remotes, and presents a cooperative state-machine API via `ca_sync_step()`. In encode mode it serializes a base tree/file/block device through `CaEncoder`, optionally emits an archive stream/file, chunks payload data into content-addressed chunks, writes chunk index records, pushes remote archive/index/chunk data, and uses `CaCache` to skip re-reading unchanged source regions. In decode mode it drives `CaDecoder`, supplies requested chunks from seeds/stores/remotes or raw archive data, supports seeking, installs temporary output files atomically, and exposes current-entry metadata.

## Important APIs, Types, and Functions

`CaDirection` distinguishes encode and decode sessions. `CaCacheState` models the encode-side cache validation flow: off, check, verify, failed, succeeded, idle. `struct CaSync` stores almost all session state: encoder/decoder, chunker and original chunker copy, index and remote index, remote archive, local/remote writable and readable stores, seed list, cache/cache-store, fds and paths for base/boundary/archive, output temp paths, mode options, feature flags, chunk counters, cache counters, digest toggles, uid mapping, compression type, and timing counters.

Construction and lifetime are handled by `ca_sync_new_encode()`, `ca_sync_new_decode()`, private `ca_sync_new()`, and `ca_sync_unref()`. Setters configure chunk sizes, decode features (`punch_holes`, `reflink`, `hardlink`, deletion, payload, immutable handling), uid shift/range, feature flags/masks, archive/index/base/boundary/store/cache locators, seed inputs, log level, rate limiting, make/base modes, and compression type. Many setters reject invalid direction or already-started/busy state using `-ENOTTY`, `-EBUSY`, `-EINVAL`, or `-EUNATCH`.

`ca_sync_start()` is the deferred initializer. It creates temporary archive/base files when needed, constructs the encoder or decoder, transfers configured fds into them, applies feature flags and decode options, opens indexes, initializes incremental indexes for remotes, prepares same-server remote index/store optimization through a cache store, propagates digest toggles, configures seeds, stores, remotes, cache digest type, and sets `start_nsec`.

Encode path helpers include `ca_sync_step_encode()`, `ca_sync_write_chunks()`, `ca_sync_write_one_chunk()`, `ca_sync_write_final_chunk()`, `ca_sync_write_one_cached_chunk()`, `ca_sync_write_archive()`, `ca_sync_write_remote_archive()`, `ca_sync_install_archive()`, and `ca_sync_cache_get()`. Decode path helpers include `ca_sync_step_decode()`, `ca_sync_process_decoder_request()`, `ca_sync_process_decoder_seek()`, `ca_sync_process_decoder_skip()`, `ca_sync_try_hardlink()`, and `ca_sync_install_base()`.

Remote integration is split across `ca_sync_remote_prefetch()`, `ca_sync_remote_push_index()`, `ca_sync_remote_push_chunk()`, `ca_sync_remote_step_one()`, `ca_sync_remote_step()`, `ca_sync_n_remotes()`, and `ca_sync_current_remote()`. `ca_sync_poll()` exposes the remote fds/events for callers that receive `CA_SYNC_POLL`.

Chunk access APIs are `ca_sync_get_local()`, `ca_sync_get()`, `ca_sync_has_local()`, and `ca_sync_make_chunk_id()`. Metadata/stat APIs forward to the active seed, encoder, or decoder: current path/mode/target/mtime/size/uid/gid/user/group/rdev/chattr/FAT attrs/xattrs/quota project id, archive offset/chunk counts, seek operations, payload access, archive size, digest enable/get, request counters, runtime and decode timing, compression type, and cache counters.

## Control Flow

The external loop calls `ca_sync_step()` until `CA_SYNC_FINISHED` or an error. On every step the function first starts the session, then tries decode-specific prerequisites in priority order: propagate index flags to stores/seeds/remotes/decoder, advance seed indexing, prefetch remote chunks, push incremental index, push chunks requested by the remote peer, decode available data, process remote IO, and finally generate encode data. This ordering lets decode consume already available bytes before reading more remote input and lets remotes drain before the encoder generates more archive/index data.

Encode mode calls `ca_encoder_step()` and reacts to encoder statuses. Data-bearing statuses (`NEXT_FILE`, `PAYLOAD`, `DATA`) are optionally cache-checked, read through `ca_encoder_get_data()`, chunked through the rolling `CaChunker`, written to stores/index/cache, and copied to local/remote archive streams. `CA_ENCODER_FINISHED` flushes the final partial chunk, writes index EOF and installs the index, renames any temporary archive path, sends remote archive EOF, and either finishes or lets remote outputs drain.

The encode cache path is a multi-step verifier. `CA_SYNC_CACHE_CHECK` probes `CaCache` for the current source `CaLocation`. `VERIFY` compares stored origin locations against generated encoder locations and buffered origin data, consuming matching bytes without storing duplicate chunks. `SUCCEEDED` writes only the cached chunk ID/index record. `FAILED` removes the stale cache entry, seeks the encoder back to the saved location, clears buffers, restores the original chunker state, and resumes uncached generation.

Decode mode asks `ca_decoder_step()` what it needs. `REQUEST` reads the next index chunk, waits for seed indexing when required, resolves the chunk from seeds/local stores/cache store/remote stores, applies any seek skip, and feeds bytes plus origin to `ca_decoder_put_data()`. Without an index, local archive fd reads are converted to payload origins and fed directly. `SEEK` uses either `ca_index_seek()` or archive `lseek()`, and `SKIP` advances chunk skip or archive fd. `DONE_FILE` can attempt seed-based hardlink reconstruction before reporting completion. `FINISHED` installs any temporary base file.

Remote control is cooperative. Incremental remote index reads go into `ca_index_incremental_write()`, remote archive reads go to the decoder, encode-side index bytes are read from the incremental index and pushed, and same-server push-index/chunks mode handles remote missing-chunk requests.

## State and Persistence Behavior

Persistent outputs can include local archive files, local index files, local chunk stores, cache directories, and decoded base trees/files/devices. Encode archive and decode regular-file base outputs use random temporary paths and `rename()` for atomic install. `ca_sync_unref()` unlinks temporary paths if the session is destroyed before install. Open fds passed into the session are consumed by encoder/decoder or closed on unref if still owned.

The chunker is persistent in session memory and reset from `original_chunker` after cache verification failure. `buffer`, `index_buffer`, `archive_buffer`, and `compress_buffer` are reusable dynamic buffers. `buffer_origin` tracks source location provenance for data currently waiting to become a chunk. Counters track generated/reused/prefetched chunks, cache hit/miss/invalidated/added totals, and request byte totals obtained from store/seed/remote layers.

Feature flags determine digest type and supported archive features. Encode defaults to `CA_FORMAT_DEFAULT & SUPPORTED_FEATURE_MASK`; decode accepts a feature mask and later propagates index-discovered flags. Remote/index/cache/store digest types are kept aligned with the active feature flags.

## Dependencies and Integration Points

This file is central to the casync library. It depends on `CaEncoder`, `CaDecoder`, `CaIndex`, `CaRemote`, `CaStore`, `CaSeed`, `CaCache`, `CaChunker`, `CaDigest`, `CaOrigin`, `CaLocation`, `ReallocBuffer`, feature-format utilities, protocol flags, and POSIX filesystem APIs. Locator classification comes from `cautil.c` through `ca_classify_locator()`. Constants such as `BUFFER_SIZE` and supported feature masks come from `def.h`. Compression is delegated to store/remote/`ca_compress()` paths.

`casync.h` exposes the public surface. Callers are expected to configure locators/options before the first `ca_sync_step()` or seek operation starts the session. `ca_sync_poll()` integrates with event loops by collecting read/write fds from all configured remotes.

## Risks and Edge Cases

The state machine is sensitive to ordering. Starting the session freezes many options; setters must be called before `start_nsec` or before encoder/decoder creation where required. Cache verification has several correctness conditions around matching `CaLocation` metadata, buffer origins, generated byte counts, and chunker reset. A stale cache entry must be removed and the encoder must be seekable to the saved location.

Remote reuse of index/store connections depends on `ca_remote_set_*_url()` returning `-EBUSY` only for non-matching or already-fixed remote cases; misinterpreting that contract can leak partially configured remotes. Decode with remote/index data may return `CA_SYNC_POLL` while internal queues are waiting for IO or seed completion. Chunk size mismatches from stores/indexes are treated as `-EBADMSG`.

Temporary install relies on `rename()` and correct cleanup on unref. Base and boundary path mode interactions are strict and can return `-EUNATCH` if decode has no known output type. Some getters return `-ENODATA`, `-ENOTTY`, or `-ENOMEDIUM` depending on direction, feature enabled state, and whether the encoder/decoder has started.

`ca_sync_poll()` counts remote_wstore separately even when it may alias `remote_index`; `ca_sync_n_remotes()` avoids aliasing for stepping, but the poll fd array may include duplicated fds if aliases exist. This should be tested against remote reuse behavior.

## Test Signals

Useful tests include encode/decode round trips with local archive+index+store, decode from raw archive without index, remote index/store/archive combinations, same-server remote index/chunk push optimization, cache hit/miss/invalidation flows after modifying source files, atomic temp-file install and cleanup, seek by offset/path/next sibling, seed-based chunk reuse and hardlink reconstruction, digest toggles, feature-flag propagation, uid shift/range behavior, and `CA_SYNC_POLL` integration with a fake remote. Error-path tests should cover missing base mode, unsupported direction setters, chunk-size mismatch, remote failures, non-regular archive seek size acquisition, and stale cache origin metadata.
