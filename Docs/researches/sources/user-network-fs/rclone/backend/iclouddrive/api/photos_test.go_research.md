<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/photos_test.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/photos_test.go

### Purpose
`photos_test.go` is the regression suite for `photos.go`. It builds local HTTP test services and temp cache directories to validate CloudKit request flow, library discovery, cache behavior, delta application, album construction, media parsing, filename normalization/deduplication, and atomic cache writes without contacting Apple.

### Important APIs, Types, and Functions
Test helpers include `setTestCacheDir`, `newHTTPTestPhotosService`, `writeJSON`, `readJSONBody`, `testAlbumRecordJSON`, and `newUserAlbumForTest`. They exercise `GetLibraries`, `GetAlbums`, `GetPhotos`, `buildPhotos`, `parsePhotoRecords`, `classifySmartAlbums`, `GetPhotoByName`, `deduplicateFilenames`, `deltaContainsAlbumChanges`, `parseDeltaRecords`, `applyPendingDelta`, `FlushCaches`, `buildSmartAlbums`, `atomicWriteFile`, and `albumCacheKey`.

### Control Flow
The HTTP tests install handlers that inspect request paths and JSON bodies. Library tests verify that cached libraries still trigger private/shared `changes/database` rediscovery, that merge preserves existing library objects and buffered deltas, and that shared-zone failures either preserve cached zones or drop them when a per-zone probe returns `ZONE_NOT_FOUND`. Album tests confirm private-library user album failures surface and allow retry, while known SharedSync index failures return only smart albums without caching the partial result.

Media construction tests build synthetic `photoRecord` masters/assets to cover original files, Live Photo MOV companions, nil/invalid filename or download URL cases, `filenameEnc` STRING vs base64 bytes, NFC normalization, `itemType` fallback names, edited JPEG/video derivatives, slo-mo metadata-only behavior, RAW alternatives, duplicate-extension `-alt` suffixing, combined edited+RAW variants, and extensionless Live Photo names.

### State and Persistence
Tests redirect rclone's cache directory to `t.TempDir()` and verify on-disk cache files directly. They create `libraries.json`, zone `syncToken`, album cache JSON files, and confirm atomic writes leave no `.tmp`. They inspect `pendingDelta`, `cacheValid`, `photoCache`, and `lib.albums` to validate in-memory cache transitions.

### Dependencies and Integration Points
The suite uses `httptest`, rclone `fs/config/pacer/rest`, and `testify` assertions. The tests deliberately avoid real network by pointing `Session.srv` at local test servers. They integrate with package-private fields because they are in package `api`, which lets them inspect locks, pending deltas, and cache internals.

### Risks and Edge Cases Covered
The strongest risk coverage is stale cache avoidance: a paged delta failure must not serve old cached photos and must clear `pendingDelta` so future checks are not stuck. Tests also cover CloudKit deleted relation records with missing `recordType`, malformed JSON records, asset-only smart album invalidation, nested folder album invalidation, shared pointer contamination during filename dedup, and concurrent `FlushCaches` with delta application.

### Test Signals
The file is high-value evidence for Photos correctness. It exercises both pure parsing logic and HTTP/cache control flow. Running it with the Go race detector would add value for `TestFlushCaches_NoPendingDeltaRace`, whose comments explicitly reference race detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/photos_test.go -->
