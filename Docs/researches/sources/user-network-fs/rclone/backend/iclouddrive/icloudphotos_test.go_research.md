# sources/user-network-fs/rclone/backend/iclouddrive/icloudphotos_test.go

## Purpose
Provides pure unit coverage for the iCloud Photos backend and related `api` smart album definitions without requiring real iCloud service calls.

## Important APIs, Types, and Functions
Test helpers `newTestPhotosFs`, `newTestPhotosService`, and `setEmptyPhotoCaches` construct in-memory `PhotosFs` and `api.PhotosService` values. Tests cover `api.SmartAlbums`, `parseAlbumDirID`, `PhotosObject.Metadata`, `resolveAlbum`, `FindLeaf`, `ListR`, and `notifyZoneChange`.

## Control Flow
The tests build synthetic library/album trees containing smart albums, user albums, folders, child albums, nested folders, and leaf albums. They pre-populate photo caches to keep `GetPhotos` and `GetPhotoByName` on the test path rather than HTTP. `ListR` tests initialize `dircache`, call `FindRoot`, collect directory callbacks, sort results, and assert expected nested paths.

## State and Persistence
All state is in memory. The tests intentionally inject `f.photos` and dircache roots instead of creating a real iCloud client. Object metadata tests use fixed timestamps and booleans.

## Dependencies and Integration Points
Uses `testify/assert`, `testify/require`, rclone `fs`, `dircache`, and the package-internal `api.NewTestPhotosService`. It validates that Photos backend helpers align with API-layer smart album and album tree contracts.

## Risks and Edge Cases
The tests do not verify HTTP download behavior, CloudKit `LookupDownloadURL`, real cache invalidation, or concurrent album failures in `ListR`. `TestParseAlbumDirID_Exhaustive` documents that the helper accepts `"notalbum:foo:bar"` as true because it only trims a prefix when present; production safety depends on caller guards.

## Test Signals
Strong unit signals exist for nested folder traversal, metadata omission for zero dimensions, smart album filter definitions, and notification scoping. The test suite makes expected synthetic directory paths explicit, which is useful when changing path encoding or dircache behavior.
