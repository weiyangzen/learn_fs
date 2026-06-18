# sources/user-network-fs/rclone/backend/googlephotos/albums_test.go

## Purpose
This unit test file validates the Google Photos album index and its virtual directory behavior.

## Important APIs, Types, And Control Flow
`TestNewAlbums` checks map initialization. `TestAlbumsAdd` verifies normal albums, duplicate titles, subdirectory-like titles, and path-cleaned weird titles. `TestAlbumsDel` verifies ID/title removal, duplicate history retention, and path pruning. `TestAlbumsGet` and `TestAlbumsGetDirs` check lookup success and failure.

## State And Persistence
All state is in local `albums` instances built from synthetic `api.Album` values. There is no remote or filesystem persistence.

## Dependencies And Integration Points
The tests use `api.Album` and testify assertions. They directly inspect internal maps, making them precise guards for the path-index contract used by listing.

## Risks And Test Signals
The tests provide strong signals for duplicate-title stability and nested album path behavior, but they do not cover concurrent access or cache invalidation after live API changes.
