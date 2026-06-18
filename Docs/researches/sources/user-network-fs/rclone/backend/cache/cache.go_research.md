# sources/user-network-fs/rclone/backend/cache/cache.go

## Purpose
Implements rclone's deprecated `cache` backend, a wrapper around another remote that caches directory/object metadata and file chunks locally. It configures persistent DB/chunk storage, optional Plex integration, optional temporary upload staging, RC commands, change notification propagation, and most wrapper Fs operations.

## Important APIs, types, and functions
Defaults define chunk size/budget, cleanup interval, info age, read retries, worker count, memory-cache behavior, RPS limit, write caching, temp upload delay, and DB wait. `Options` maps wrapped remote, Plex settings, cache paths, purge, workers, RPS, store-writes, temp upload path, and timings. `Fs` embeds the wrapped `fs.Fs` and stores wrapper/root/options/features, `Persistent` cache, temp fs, cleanup state, rate limiter, Plex connector, background uploader, and notification state.

`NewFs` validates config, rejects self-wrapping, opens the wrapped remote, creates DB/chunk directories, opens `Persistent`, configures Plex/temp uploads, starts background cleanup/upload workers, subscribes to wrapped change notifications, masks/wraps features, and registers RC calls. `NewObject`, `List`, `ListR`, `Mkdir`, `Rmdir`, `DirMove`, shared `put`, `Put`, `PutUnchecked`, `PutStream`, `Copy`, `Move`, `Purge`, `CleanUp`, `Stats`, `CleanUpCache`, and `StopBackgroundRunners` are the main operational methods.

## Control flow
Reads first consult warm persistent metadata under `InfoAge`, then probe temp fs and/or wrapped source and persist refreshed objects. Listings merge queued temp-upload entries with source entries, remove stale cached entries, persist source objects/directories, and refresh directory timestamps. Writes either stage to temp fs and queue background upload, tee through `cacheReader` to store chunks, or delegate directly. Mutations expire parent directories and notify upstreams. Temp upload move/delete operations pause the uploader and reconcile pending upload records.

## State and persistence
Local persistent state includes `<db_path>/<remote>.db`, chunk files under `<chunk_path>/<remote>`, pending upload metadata, cached directory entries, cached object metadata, and cached chunks. Remote persistent state remains in the wrapped fs. Runtime state includes cleanup goroutine, optional uploader, Plex websocket, rate limiter, RC handlers, subscribers, and notified-remote map.

## Dependencies and integration points
Integrates with rclone config, `fs/cache` remote construction/pinning, feature wrapping/masking, `rc`, `walk`, `crypt`, sibling cache `Persistent`/`Object`/`Directory` helpers, Plex connector/background writer code, and `rate.Limiter`. Receives change notifications from wrapped remotes and forwards invalidations to wrappers such as VFS.

## Risks
Deprecated and complex. Stale metadata depends on `InfoAge`, change notifications, or manual expiry. Temp upload mode has races around move/delete while background uploads are pending or active. `StopBackgroundRunners` can block on a full cleanup channel if called repeatedly. RC calls are registered globally per Fs instance. `Purge` has a FIXME for root prefixes. `Shutdown` delegates to the wrapped fs but does not stop cache background runners. Path normalization and crypt name conversion are delicate.

## Test signals
No tests are listed for this file in the work item. Interface assertions document support for purger, copier, mover, dir mover, put unchecked/streaming, cleaner, wrapper/unwrapper, recursive lister, change notifier, abouter, user info, disconnect, commander, merge dirs, and shutdown.
