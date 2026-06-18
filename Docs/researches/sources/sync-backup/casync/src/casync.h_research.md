# sources/sync-backup/casync/src/casync.h

## Purpose

`casync.h` is the public API for the opaque `CaSync` synchronization object. It defines the cooperative status codes returned by `ca_sync_step()`, construction/destruction functions, configuration setters for encode/decode sessions, locator setup for archives/indexes/stores/seeds/cache, state-machine polling, metadata accessors, low-level chunk retrieval, seeking, digest control, and statistics getters.

## Important APIs, Types, and Functions

The header forward-declares `CaSync` and includes chunk, chunk-id, common compression/iteration types, and origin definitions. The status enum maps internal encoder/decoder/seed/remote statuses to public values: `CA_SYNC_FINISHED`, `CA_SYNC_STEP`, `CA_SYNC_PAYLOAD`, file boundary events, seed file events, `CA_SYNC_POLL`, and seek-found/not-found events.

Creation is split by direction with `ca_sync_new_encode()` and `ca_sync_new_decode()`. `ca_sync_unref()` integrates with the local cleanup macro. Configuration APIs include log level, rate limiting, feature flags/mask, decode output behavior (`punch_holes`, `reflink`, `hardlink`, deletion, payload, immutable handling), compression type, uid mapping, output creation mode, index/base/boundary/archive/store locators, additional stores, seeds, and cache.

Runtime APIs are `ca_sync_step()` and `ca_sync_poll()`. Metadata APIs expose current path, mode, target, uid/gid, user/group, mtime, size, rdev, chattr, FAT attrs, xattrs, quota project id, archive size, archive chunk counters, archive offset, payload bytes, punch/reflink/hardlink counters, and cache counters. Low-level chunk APIs expose local/all-store lookup, existence checks, and chunk ID generation. Seeking APIs allow offset, path, path+offset, and next sibling navigation in decode mode. Digest APIs enable and retrieve archive, payload, and hardlink digests. Statistics APIs report seed/local/remote request counts, bytes, seeding time, decoding time, and total runtime.

## Control Flow

The intended call pattern is configure a new object, repeatedly call `ca_sync_step()`, call `ca_sync_poll()` when `CA_SYNC_POLL` is returned and remotes exist, inspect metadata on file/payload events, optionally call seek methods in decode mode, then unref the object. Many getters are meaningful only after the underlying encoder/decoder/seed has reached a state where the requested data exists.

## State and Persistence Behavior

The header hides `struct CaSync`; callers interact only through setter/getter side effects. Fd setters transfer ownership to the object implementation. Path/remote locators are stored internally until start, when local files may be opened or created and remote objects initialized. The cleanup macro encourages scoped ownership.

## Dependencies and Integration Points

The API integrates with the rest of casync through `CaChunkID`, `CaChunkCompression`, `CaCompressionType`, `CaIterate`, and `CaOrigin`. Higher-level CLI or library users build sync workflows from this header. Event loops use `ca_sync_poll()` with `sigset_t`.

## Risks and Edge Cases

Because the object is direction-specific, callers must expect `-ENOTTY` for encode-only or decode-only operations used incorrectly. Several options must be set before start; late calls can fail. Fd ownership needs clear caller discipline to avoid double close. Return values are mixed status codes and negative errno-style errors, so callers must not treat every nonzero as failure.

## Test Signals

Compile-time tests should include API availability for C users and cleanup macro use. Behavioral tests should cover each status code, setter validation by direction, ownership of fd/path locators, `CA_SYNC_POLL` with and without remotes, metadata getters before and after file events, digest enable/get combinations, and stats getters before start and after completion.
