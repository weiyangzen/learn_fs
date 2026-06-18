<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/cache.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/cache.go

Source read: complete file, 77 lines, 1399 bytes, sha256 `8ec5a9022f80fa85fff40c3f2e0a88cf69a12d28000b025f8a9d63d2333a96ca`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/cache.go_research.md`.

## Purpose
Implements a small optional in-memory cache of restic repository objects to speed repeated object reads after list operations.

## Important APIs, types, and functions
`cache` contains an RW mutex, `map[string]fs.Object`, and a `cacheObjects` switch. `newCache`, `find`, `add`, `remove`, and `removePrefix` are the public-in-package operations.

## Control flow
Server paths call `find` before `Fs.NewObject`, add objects after successful upload/list discovery, remove on delete, and clear descendants before refreshing directory listings.

## State and persistence behavior
State is process-memory only and disappears on restart. When disabled, all operations become no-ops or misses. `removePrefix("/")` clears the entire cache.

## Dependencies and integration points
Depends on `sync`, string prefix checks, and `fs.Object`.

## Risks and edge cases
Prefix removal intentionally appends `/`, so removing `b` preserves an exact object named `b` while deleting children. Stale objects are possible if external writers mutate the backend outside restic list/delete/upload flows.

## Test signals
`cache_test.go` validates CRUD and prefix-removal semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/cache.go -->
