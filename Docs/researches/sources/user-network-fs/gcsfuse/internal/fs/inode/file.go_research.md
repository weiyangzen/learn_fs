# sources/user-network-fs/gcsfuse/internal/fs/inode/file.go

## Purpose

`file.go` implements `FileInode`, the inode representation for regular GCS-backed or local-not-yet-synced files. It provides FUSE-facing file identity, attributes, reads, writes, truncation, mtime updates, flush/sync, lookup count handling, local unlink state, content cache integration, and streaming-write support. Its core job is to reconcile three states: the remote GCS source object (`src`), local staged temp-file content (`content`), and optional buffered streaming writes (`bwh`).

## Important APIs, Types, And Functions

`FileInode` stores dependencies (`SyncerBucket`, clocks, content cache, config, tracing, metrics, semaphores), immutable identity (`id`, `name`, base attrs), and mutable state guarded by `syncutil.InvariantMutex`. The important mutable fields are `src`, `content`, `local`, `unlinked`, `bwh`, `writeHandleCount`, MRD/kernel reader instances, and `lookupCount`.

`NewFileInode` initializes state, lookup counts, invariant checking, and either rapid-bucket multi-range downloader wrappers or a kernel range reader instance. `checkInvariants` enforces legal file names, non-local source-name matching, and temp-file invariants. `clobbered` stats GCS and compares `Generation` values; equal gen/metagen with larger remote size returns compare code `2` and is treated as a remote append clobber for sync but as an attribute size refresh in `Attributes`.

Read path functions include `openReader`, `ensureContent`, `Read`, and `CacheEnsureContent`. Write path functions include `Write`, `writeUsingTempFile`, `writeUsingBufferedWrites`, `flushUsingBufferedWriteHandler`, `SyncPendingBufferedWrites`, `Sync`, `Flush`, `syncUsingContent`, `Truncate`, and BWH initialization via `InitBufferedWriteHandlerIfEligible`/`areBufferedWritesSupported`.

## Control Flow And State Behavior

Reads are disallowed while streaming writes are in progress. Otherwise `Read` ensures local content exists, either from persistent content cache or a new temp file opened from the exact source generation, then reads from that temp file. Writes use BWH when available; otherwise they fault in temp content and write locally. Out-of-order streaming writes finalize the buffered object, record a fallback metric, then fall back to temp-file staging for the triggering write.

`Sync` and `Flush` are no-ops for clean files. With BWH, `Sync` only uploads pending buffers and may return a `MinObject` for zonal/rapid buckets; `Flush` finalizes and clears BWH. With staged content, `syncUsingContent` optionally fetches the latest GCS object, rejects clobbers, uploads via `SyncObject`, validates uploaded size, then updates `src`, reader wrappers, local/non-local state, and destroys temp content.

Attributes derive from base attrs plus source object metadata. `goog-reserved-file-mtime` is honored, then `gcsfuse_mtime` overrides it. Temp content and BWH state override size/mtime. Clobber checking can set `Nlink` to zero, or update inode size when only remote append size increased at the same generation. Local unlinked files also expose `Nlink` zero.

## Dependencies And Integration Points

The file integrates with `gcsx.SyncerBucket`, `gcs` requests/errors, `storageutil` object conversion, `contentcache`, `bufferedwrites`, `block` allocation limits, `kernel_readers`, `lru` MRD cache, `gcsfuse_errors.FileClobberedError`, `metrics`, `tracing`, FUSE attributes, and `cfg.WriteConfig`. It is a central dependency of file handle operations, directory-created local files, content cache paths, and rapid/zonal write semantics.

## Risks And Test Signals

Risks concentrate around clobber semantics, BWH lifecycle, generation-size comparison for zonal appends, local-file promotion after sync, temp-file cleanup, persistent content-cache invalidation, and reader wrapper min-object updates. There are also subtle differences between `Sync` and `Flush` for streaming writes and between rapid append versus overwrite metadata fetching. The requested test files cover read/write/truncate/mtime behavior, clobber errors, mock bucket request patterns, zonal versus non-zonal streaming writes, BWH fallback, local unlink handling, upload-size validation, and file-handle deregistration.
