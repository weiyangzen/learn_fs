# sources/sync-backup/kopia/repo/blob/gdrive/file_id_cache.go

Purpose: implements a concurrency-safe cache mapping Kopia blob IDs to Google Drive file IDs, plus a small circular change log.

Important APIs/types/functions: `fileIDCache`, `cacheEntry`, `changeEntry`, `Lookup`, `getEntry`, `BlindPut`, `RecordBlobChange`, `VisitBlobChanges`, `Clear`, `circularBufferNext`, and `newFileIDCache`.

Control flow: `Lookup` fetches or creates a cache entry from `sync.Map`, locks that entry, and gives exclusive access to the callback. `BlindPut` uses `Lookup` to set a file ID. `RecordBlobChange` writes blob/fileID changes into a fixed circular buffer protected by `mu`. `VisitBlobChanges` iterates the buffer from oldest-ish to newest and skips empty entries. `Clear` resets both map and change log.

State and persistence behavior: all cache state is in memory. It is not persisted across process restarts. The change log helps `ListBlobs` compensate for Google Drive prefix-query limitations and eventual list omissions.

Dependencies/integration points: used exclusively by `gdrive_storage.go`. Risks include fixed 256-entry change log dropping older unvisited changes, no cleanup of per-blob map entries except `Clear`, and iteration order of the circular buffer being subtle. Tests cover behavior indirectly through GDrive storage integration tests.
