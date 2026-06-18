# sources/user-network-fs/rclone/backend/googlephotos/albums.go

## Purpose
This file implements an in-memory album index for the Google Photos backend. It converts Google Photos flat album titles into a stable virtual directory tree and handles duplicate album titles.

## Important APIs, Types, And Control Flow
The `albums` type stores `dupes` by original title, `byID`, `byTitle`, and `path` mappings for partial directory paths. `newAlbums` initializes the maps. `add` cleans album titles, substitutes an ID-only title for empty/root-like titles, and calls `_add` under lock. `_add` tracks duplicates; when the second duplicate appears it removes and re-adds the first album so both visible names include `{ID}`, then indexes the album and records each parent path component. `del` and `_del` remove ID/title mappings and prune path entries while intentionally leaving `dupes` intact so duplicate naming remains stable. `get` and `getDirs` are locked readers.

## State And Persistence
State is process-local and protected by a mutex. It mirrors remote album metadata but does not persist locally. Deletions remove lookup/path state but leave duplicate history to avoid renaming albums after one duplicate disappears.

## Dependencies And Integration Points
It depends on Google Photos API `Album`, `path.Clean`, string path splitting, slices deletion, and the package helper `addID`. `googlephotos.go` uses it as the cached result of `listAlbums`, while `pattern.go` uses `get` and `getDirs` to synthesize album directories and album contents.

## Risks And Test Signals
Risks include stale album cache invalidation, mutation of `album.Title` while adding, stable duplicate naming after deletion, and path pruning when an album title is both a directory prefix and an album. Unit tests cover add, delete, duplicate naming, weird cleaned paths, title lookup, and directory lookup.
