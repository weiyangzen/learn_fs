<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/photos.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/photos.go

### Purpose
`photos.go` implements the CloudKit-facing iCloud Photos service used by the rclone Photos backend. It discovers photo libraries/zones, builds smart and user album models, lists media through CloudKit records/query partitions, caches libraries/albums/photos/sync tokens on disk, applies incremental changes/zone deltas when possible, classifies smart album membership, builds file entries for originals/Live Photo companions/edited derivatives/RAW alternatives, and resolves fresh download URLs.

### Important APIs, Types, and Functions
Top-level service types are `PhotosService`, `Library`, `Album`, `Photo`, and `Filter`. Construction happens through `NewPhotosService`; tests can use `NewTestPhotosService` and `Album.SetTestPhotoCache`. Library APIs include `GetLibraries`, `GetLibraryAlbumCounts`, `PollForChanges`, `resolveZone`, and `LookupDownloadURL`. Library methods include `GetAlbums`, `GetAlbumCounts`, `checkForChanges`, `applyPendingDelta`, `saveSyncToken`, `readSyncToken`, `zoneIDMap`, and cache invalidation helpers. Album methods include `GetPhotos`, `GetPhotoByName`, `fetchPhotoCount`, `fetchPhotosParallel`, `buildPartitionQuery`, and disk-cache load/save helpers.

Important parsing helpers are `parsePhotoRecords`, `buildPhotos`, `classifySmartAlbums`, `deduplicateFilenames`, `parseDeltaRecords`, `deltaContainsAlbumChanges`, `relationAlbumRecordFromRecordName`, and `albumCacheKey`. CloudKit model structs include `albumRecord`, `albumQueryResponse`, `changesZoneResponse`, `changesZoneResult`, `deltaParseResult`, `photoRecord`, and typed field wrappers such as `ckStringField`, `ckResourceField`, and `ckReferenceField`.

### Control Flow
`NewPhotosService` verifies the `ckdatabasews` webservice is active, builds the CloudKit database root URL, and probes indexing state. `GetLibraries` first returns in-memory libraries if present, but still attempts rediscovery and merge. With disk cache, it loads `libraries.json`, batch-checks zone deltas, then attempts rediscovery; with no cache, it discovers zones from private and shared `changes/database`. Discovery admits only `PrimarySync` and `SharedSync*` zones.

`GetAlbums` returns cached in-memory albums, then disk `albums.json` if `cacheValid` is true, otherwise constructs smart album templates and fetches paginated user albums (`CPLAlbumByPositionLive`). Folder albums recursively query children by `parentId`. Shared libraries with the known invalid index error fall back to smart albums only. `GetPhotos` first checks and applies deltas, then serves memory or disk photo caches. If cache is unavailable/currentness cannot be proven, it fetches counts and performs parallel start-rank partition queries, with tail probing for stale or zero counts.

### State and Persistence
Photos state lives under `Client.CacheDir()`: `libraries.json`, per-zone `albums.json`, per-zone `syncToken`, and per-album photo caches named by a 16-hex-character SHA256 prefix of the album object type. Writes use temp-file plus rename via `atomicWriteFile`. `PhotosService.mu` protects the service library map, `Library.mu` protects albums, `Library.deltaMu` serializes pending delta application, and each `Album.mu` protects filename-keyed `photoCache`. `Library.cacheValid` is atomic and marks whether disk caches can be used.

Delta handling buffers the first changed page from `changes/zone` until albums are populated. It then drains remaining pages, classifies deleted IDs, new master/asset pairs, album membership changes, and asset-only metadata updates. It incrementally updates unaffected cached albums, invalidates affected user or smart album caches, clears album metadata cache on `CPLAlbum` changes, and advances the sync token only after successful application.

### Dependencies and Integration Points
The code depends on rclone `fs`, `pacer`, and `rest`, the shared `Client`/`Session` auth layer, CloudKit private/shared database endpoints, and `golang.org/x/text/unicode/norm` for NFC filename normalization. It integrates with rclone checkers for parallelism and with backend ChangeNotify through `PollForChanges`, which intentionally uses a separate in-memory notification token.

### Risks and Edge Cases
This is the highest-risk file in the subset. It relies on undocumented CloudKit record types, index names, field names, and Apple-specific error strings. Cache correctness depends on careful sync-token advancement and lock ordering. Some deltas cannot be safely applied and force cache invalidation. Empty or malformed Apple responses can degrade listing completeness or return errors. Filename dedup mutates `Photo` objects, so shared pointers must be copied before dedup. `GetPhotos` may issue many partition queries for large libraries and depends on server behavior that 200 records equal about 100 photos. Shared-library discovery must distinguish transient shared database failures from authoritative `ZONE_NOT_FOUND`.

### Test Signals
`photos_test.go` provides substantial regression coverage for stale-cache prevention on paged delta failure, library rediscovery and merge behavior, shared-zone preservation/drop decisions, user album retry behavior, smart-album fallback, folder child retry, media variant construction, NFC normalization, filename fallback, smart album classification, dedup stability, delta parsing, nested album invalidation, `FlushCaches` race safety, smart-album table shape, atomic writes, and album cache-key determinism.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/photos.go -->
